"""Long-poll Telegram updates and pass text to the shared application."""

import asyncio
import logging
from collections import deque

from saba_et.application import SabaApplication
from saba_et.telegram.api import TelegramAPIError, TelegramBotClient
from saba_et.database import database_url
from saba_et.telegram_jobs import TelegramJobQueue

logger = logging.getLogger(__name__)


class TelegramTransport:
    def __init__(self, client: TelegramBotClient, application: SabaApplication) -> None:
        self._client = client
        self._application = application
        self._user_locks: dict[int, asyncio.Lock] = {}
        self._update_tasks: set[asyncio.Task[None]] = set()
        self._recent_update_ids: deque[int] = deque(maxlen=2_000)
        self._recent_update_id_set: set[int] = set()
        self._job_queue = TelegramJobQueue() if database_url() else None
        self._queue_worker: asyncio.Task[None] | None = None

    async def run(self) -> None:
        offset: int | None = None
        logger.info("Saba Telegram polling started")
        retry_delay = 2
        while True:
            try:
                updates = await self._client.get_updates(offset)
                retry_delay = 2
                for update in updates:
                    offset = update["update_id"] + 1
                    self.enqueue_update(update)
            except TelegramAPIError as exc:
                logger.warning("Telegram request failed (%s); retrying in %s seconds", str(exc), retry_delay)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)

    def start(self) -> None:
        """Start recovering durable webhook jobs after process startup."""
        if self._job_queue and (self._queue_worker is None or self._queue_worker.done()):
            self._queue_worker = asyncio.create_task(self._drain_durable_jobs())

    def enqueue_update(self, update: dict) -> bool:
        """Schedule one update once; used by webhook delivery and polling."""
        if self._job_queue:
            inserted = self._job_queue.enqueue(update)
            if inserted:
                if self._queue_worker is None or self._queue_worker.done():
                    self._queue_worker = asyncio.create_task(self._drain_durable_jobs())
            return inserted
        update_id = update.get("update_id")
        if isinstance(update_id, int):
            if update_id in self._recent_update_id_set:
                return False
            if len(self._recent_update_ids) == self._recent_update_ids.maxlen:
                expired = self._recent_update_ids.popleft()
                self._recent_update_id_set.discard(expired)
            self._recent_update_ids.append(update_id)
            self._recent_update_id_set.add(update_id)
        task = asyncio.create_task(self._process_update(update))
        self._update_tasks.add(task)
        task.add_done_callback(self._update_tasks.discard)
        return True

    async def close(self) -> None:
        """Give in-flight handlers a short chance to finish during shutdown."""
        if self._queue_worker is not None:
            self._queue_worker.cancel()
            await asyncio.gather(self._queue_worker, return_exceptions=True)
        tasks = tuple(self._update_tasks)
        if not tasks:
            return
        try:
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=8)
        except TimeoutError:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _drain_durable_jobs(self) -> None:
        """Consume queued/recovered updates sequentially; the database is the source of truth."""
        assert self._job_queue is not None
        while True:
            try:
                job = await asyncio.to_thread(self._job_queue.claim)
            except Exception:
                logger.exception("Could not claim Telegram job")
                await asyncio.sleep(2)
                continue
            if job is None:
                await asyncio.sleep(0.5)
                continue
            await self._process_update(job["payload"])
            try:
                await asyncio.to_thread(self._job_queue.finish, job["id"])
            except Exception:
                logger.exception("Could not finalize Telegram job")
                return

    async def _process_update(self, update: dict) -> bool:
        message = update.get("message", {})
        user = message.get("from", {})
        user_id = user.get("id")
        if not isinstance(user_id, int):
            return True
        lock = self._user_locks.setdefault(user_id, asyncio.Lock())
        async with lock:
            try:
                await self._handle_update(update)
            except TelegramAPIError as exc:
                logger.warning("Could not handle Telegram update for user %s (%s).", user_id, str(exc))
                return False
            except Exception:
                logger.exception("Unexpected error while handling Telegram update for user %s.", user_id)
                return False
        return True

    async def _handle_update(self, update: dict) -> None:
        message = update.get("message", {})
        chat = message.get("chat", {})
        user = message.get("from", {})
        text = message.get("text")
        if not text or "id" not in chat or "id" not in user:
            return
        user_id = user["id"]
        status_message_id: int | None = None
        progress_started = asyncio.get_running_loop().time()
        progress_stage = "search"
        agent_request = self._application.requires_agent(user_id, text)
        if agent_request:
            try:
                await self._client.send_chat_action(chat["id"], "typing")
            except TelegramAPIError:
                logger.debug("Could not send Telegram typing indicator")
            try:
                status_message_id = await self._client.send_message(
                    chat["id"], f"{self._application.progress_label(user_id, progress_stage)} [0s]"
                )
            except TelegramAPIError:
                logger.debug("Could not send Telegram research status")

        async def progress(stage: str) -> None:
            nonlocal progress_stage
            if status_message_id is None:
                return
            progress_stage = stage
            try:
                await self._client.send_chat_action(chat["id"], "typing")
                await self._client.edit_message_text(
                    chat["id"],
                    status_message_id,
                    f"{self._application.progress_label(user_id, stage)} [{int(asyncio.get_running_loop().time() - progress_started)}s]",
                )
            except TelegramAPIError:
                logger.debug("Could not update Telegram research status")

        async def update_elapsed_time() -> None:
            while status_message_id is not None:
                await asyncio.sleep(5)
                elapsed = int(asyncio.get_running_loop().time() - progress_started)
                try:
                    await self._client.edit_message_text(
                        chat["id"],
                        status_message_id,
                        f"{self._application.progress_label(user_id, progress_stage)} [{elapsed}s]",
                    )
                except TelegramAPIError:
                    logger.debug("Could not update Telegram elapsed-time status")
                    return

        elapsed_task = asyncio.create_task(update_elapsed_time()) if status_message_id is not None else None
        try:
            reply = await self._application.handle(user_id, text, on_progress=progress if agent_request else None)
        finally:
            if elapsed_task is not None:
                elapsed_task.cancel()
                await asyncio.gather(elapsed_task, return_exceptions=True)
            if status_message_id is not None:
                try:
                    await self._client.delete_message(chat["id"], status_message_id)
                except TelegramAPIError:
                    logger.debug("Could not remove completed Telegram research status")
        await self._client.send_message(chat["id"], reply.text, reply.buttons)

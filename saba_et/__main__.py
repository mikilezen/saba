"""Run the Saba Telegram bot."""

import asyncio
import logging
import os
from pathlib import Path

from saba_et.agent import GovernmentServiceAgent
from saba_et.application import SabaApplication
from saba_et.audit import AuditLog
from saba_et.config import Settings
from saba_et.env import load_env_file
from saba_et.knowledge import ServiceCatalog
from saba_et.profile_store import ProfileStore
from saba_et.task_store import TaskStore
from saba_et.provider_directory import ProviderDirectory
from saba_et.vapi import VapiCallLedger, VapiSettings, load_voice_contacts
from saba_et.telegram.api import TelegramAPIError, TelegramBotClient
from saba_et.telegram.transport import TelegramTransport


def create_runtime():
    """Build shared Saba components for polling and webhook entry points."""
    project_root = Path(__file__).resolve().parent.parent
    load_env_file(project_root / ".env")
    try:
        settings = Settings.from_env()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    catalog = ServiceCatalog(project_root / "data" / "services.json")
    provider_directory = ProviderDirectory(project_root / "data" / "providers.json")
    database_dir = Path(os.environ.get("SABA_DATA_DIR", str(project_root / "data")))
    database_path = database_dir / "saba.sqlite3"
    database_dir.mkdir(parents=True, exist_ok=True)
    call_ledger = VapiCallLedger(database_path)
    audit_log = AuditLog(database_path)
    profile_store = ProfileStore(database_path)
    task_store = TaskStore(database_path)
    agent = None
    if os.environ.get("GEMINI_API_KEY"):
        try:
            agent = GovernmentServiceAgent(
                catalog,
                model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                provider_directory=provider_directory,
                vapi_settings=VapiSettings.from_env(),
                voice_contacts=load_voice_contacts(project_root / "data" / "voice_contacts.json"),
                call_ledger=call_ledger,
            )
        except (ImportError, ValueError) as exc:
            detail = str(exc) or type(exc).__name__
            raise SystemExit(
                f"Could not configure Saba's agent: {detail}. "
                "Install requirements in this Python environment and check GEMINI_API_KEY."
            ) from None
    else:
        logging.getLogger(__name__).warning("GEMINI_API_KEY was not found in the project .env file or process environment; autonomous search replies will be unavailable")
    application = SabaApplication(catalog, audit_log, agent, profile_store, provider_directory, task_store)
    application.vapi_call_ledger = call_ledger
    client = TelegramBotClient(
        settings.telegram_bot_token,
        settings.telegram_api_base,
        settings.request_timeout_seconds,
    )
    return settings, application, client, profile_store


async def set_bot_name(client: TelegramBotClient, profile_store: ProfileStore) -> None:
    if profile_store.is_configured("telegram_bot_name_saba_et"):
        return
    try:
        await client.set_my_name("Saba ET")
        profile_store.mark_configured("telegram_bot_name_saba_et")
    except TelegramAPIError as exc:
        logging.getLogger(__name__).warning("Could not update Telegram bot name (%s)", str(exc))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings, application, client, profile_store = create_runtime()

    async def run() -> None:
        await client.start()
        try:
            # Polling and webhooks cannot be enabled for the same bot at once.
            retry_delay = 2
            while True:
                try:
                    await client.delete_webhook(drop_pending_updates=False)
                    break
                except TelegramAPIError as exc:
                    logging.getLogger(__name__).warning(
                        "Could not reach Telegram to prepare polling (%s); retrying in %s seconds",
                        str(exc),
                        retry_delay,
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 30)
            await set_bot_name(client, profile_store)
            await TelegramTransport(client, application).run()
        finally:
            await client.close()

    asyncio.run(run())


if __name__ == "__main__":
    main()

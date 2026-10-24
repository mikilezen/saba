"""Async Telegram Bot API client with connection pooling."""

import socket
import ssl
from typing import Any

import httpx


class TelegramAPIError(RuntimeError):
    pass


class TelegramBotClient:
    def __init__(self, token: str, api_base: str, timeout: int = 25) -> None:
        self._base = f"{api_base.rstrip('/')}/bot{token}"
        self._poll_timeout = timeout
        self._session: httpx.AsyncClient | None = None

    async def start(self) -> None:
        """Open a reusable connection pool before polling begins."""
        if self._session is None:
            self._session = httpx.AsyncClient(
                timeout=httpx.Timeout(connect=5, read=12, write=10, pool=5),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )

    async def close(self) -> None:
        if self._session is not None:
            await self._session.aclose()
            self._session = None

    async def call(self, method: str, payload: dict[str, Any]) -> Any:
        if self._session is None:
            await self.start()
        assert self._session is not None
        request_options = {}
        if method == "getUpdates":
            request_options["timeout"] = httpx.Timeout(
                connect=5, read=self._poll_timeout + 10, write=10, pool=5
            )
        try:
            response = await self._session.post(
                f"{self._base}/{method}", json=payload, **request_options
            )
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPStatusError as exc:
            raise TelegramAPIError(f"Telegram {method} returned HTTP {exc.response.status_code}.") from None
        except httpx.ConnectTimeout:
            raise TelegramAPIError(f"Telegram {method} connection timed out.") from None
        except httpx.ReadTimeout:
            raise TelegramAPIError(f"Telegram {method} response timed out.") from None
        except httpx.TimeoutException:
            raise TelegramAPIError(f"Telegram {method} request timed out.") from None
        except httpx.ConnectError as exc:
            reason = exc.__cause__
            if isinstance(reason, socket.gaierror):
                detail = "DNS lookup failed"
            elif isinstance(reason, ssl.SSLError):
                detail = "TLS handshake failed"
            else:
                detail = "network unavailable"
            raise TelegramAPIError(f"Telegram {method} network error: {detail}.") from None
        except (httpx.NetworkError, httpx.RemoteProtocolError, ValueError):
            raise TelegramAPIError(f"Telegram {method} network or response error.") from None
        if not isinstance(result, dict) or not result.get("ok"):
            raise TelegramAPIError(f"Telegram {method} returned an error.")
        return result["result"]

    async def get_updates(self, offset: int | None) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {"timeout": self._poll_timeout, "allowed_updates": ["message"]}
        if offset is not None:
            payload["offset"] = offset
        return await self.call("getUpdates", payload)

    async def set_webhook(self, url: str, secret_token: str) -> None:
        await self.call(
            "setWebhook",
            {
                "url": url,
                "secret_token": secret_token,
                "allowed_updates": ["message"],
                "max_connections": 5,
                "drop_pending_updates": False,
            },
        )

    async def delete_webhook(self, drop_pending_updates: bool = False) -> None:
        await self.call("deleteWebhook", {"drop_pending_updates": drop_pending_updates})

    async def send_message(self, chat_id: int, text: str, buttons: tuple[tuple[str, ...], ...] = ()) -> int:
        payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if buttons:
            payload["reply_markup"] = {
                "keyboard": [[{"text": label} for label in row] for row in buttons],
                "resize_keyboard": True,
            }
        else:
            payload["reply_markup"] = {"remove_keyboard": True}
        result = await self.call("sendMessage", payload)
        return int(result["message_id"])

    async def set_my_name(self, name: str) -> None:
        await self.call("setMyName", {"name": name})

    async def edit_message_text(self, chat_id: int, message_id: int, text: str) -> None:
        await self.call("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    async def delete_message(self, chat_id: int, message_id: int) -> None:
        await self.call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def send_chat_action(self, chat_id: int, action: str = "typing") -> None:
        await self.call("sendChatAction", {"chat_id": chat_id, "action": action})

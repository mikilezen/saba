"""Render ASGI application for secure Telegram webhook delivery."""

from __future__ import annotations

from contextlib import asynccontextmanager
import base64
import binascii
import hmac
import json
import logging
import os
import re
import time
from typing import AsyncIterator
from uuid import uuid4

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx

from saba_et.__main__ import create_runtime, set_bot_name
from saba_et.telegram.transport import TelegramTransport
from saba_et.database import database_url

logger = logging.getLogger(__name__)
MAX_WEBHOOK_BODY_BYTES = 1_000_000
SECRET_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,256}\Z")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if not database_url():
        raise RuntimeError("Set SUPABASE_DB_URL for hosted webhook mode; SQLite is for local development only.")
    _, application, client, profile_store = create_runtime()
    webhook_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
    public_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip().rstrip("/")
    if not SECRET_TOKEN_PATTERN.fullmatch(webhook_secret):
        raise RuntimeError("Set TELEGRAM_WEBHOOK_SECRET to 1–256 letters, numbers, underscores, or hyphens.")
    if not public_url.startswith("https://"):
        raise RuntimeError("RENDER_EXTERNAL_URL must be an HTTPS URL before enabling Telegram webhooks.")

    transport = TelegramTransport(client, application)
    vapi_secret = os.environ.get("VAPI_WEBHOOK_SECRET", "").strip()
    await client.start()
    try:
        await client.set_webhook(f"{public_url}/telegram/webhook", webhook_secret)
        await set_bot_name(client, profile_store)
        app.state.transport = transport
        transport.start()
        app.state.telegram_webhook_secret = webhook_secret
        app.state.vapi_webhook_secret = vapi_secret
        app.state.telnyx_api_key = os.environ.get("TELNYX_API_KEY", "").strip()
        app.state.telnyx_public_key = os.environ.get("TELNYX_PUBLIC_KEY", "").strip()
        app.state.vapi_call_ledger = application.vapi_call_ledger
        app.state.telegram_client = client
        logger.info("Saba Telegram webhook configured")
        yield
    finally:
        await transport.close()
        await client.close()


app = FastAPI(title="Saba ET Telegram Webhook", lifespan=lifespan)


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    provided_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    expected_secret = getattr(request.app.state, "telegram_webhook_secret", "")
    if not expected_secret or not hmac.compare_digest(provided_secret, expected_secret):
        raise HTTPException(status_code=403, detail="Forbidden")

    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_WEBHOOK_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large")
    body = await request.body()
    if len(body) > MAX_WEBHOOK_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large")
    try:
        update = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid JSON") from None
    if not isinstance(update, dict) or not isinstance(update.get("update_id"), int):
        raise HTTPException(status_code=400, detail="Invalid Telegram update")

    transport: TelegramTransport = request.app.state.transport
    transport.enqueue_update(update)
    return JSONResponse({"ok": True})


@app.post("/vapi/webhook")
async def vapi_webhook(request: Request) -> JSONResponse:
    expected_secret = getattr(request.app.state, "vapi_webhook_secret", "")
    provided_secret = request.headers.get("X-Saba-Vapi-Secret", "")
    if not expected_secret or not hmac.compare_digest(provided_secret, expected_secret):
        raise HTTPException(status_code=403, detail="Forbidden")
    body = await request.body()
    if len(body) > MAX_WEBHOOK_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large")
    try:
        envelope = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid JSON") from None
    message = envelope.get("message", {}) if isinstance(envelope, dict) else {}
    if not isinstance(message, dict) or message.get("type") != "end-of-call-report":
        return JSONResponse({"ok": True, "ignored": True})
    call = message.get("call", {})
    call_id = call.get("id") if isinstance(call, dict) else None
    if not isinstance(call_id, str) or not call_id:
        return JSONResponse({"ok": True, "ignored": True})
    user_id = request.app.state.vapi_call_ledger.finish(call_id)
    if user_id is None:
        return JSONResponse({"ok": True, "duplicate_or_unknown": True})
    analysis = call.get("analysis", {}) if isinstance(call, dict) else {}
    summary = analysis.get("summary", "") if isinstance(analysis, dict) else ""
    summary = re.sub(r"\b\d{5,}\b", "[redacted number]", str(summary))
    summary = re.sub(r"\s+", " ", summary).strip()[:1000]
    if not summary:
        summary = "The call ended. Vapi did not provide a summary."
    await request.app.state.telegram_client.send_message(
        chat_id=user_id,
        text=f"Vapi call update:\n{summary}",
    )
    return JSONResponse({"ok": True})


def verify_telnyx_signature(body: bytes, signature: str, timestamp: str, public_key: str) -> bool:
    """Verify Telnyx's Ed25519 signature over ``timestamp|raw_body``."""
    try:
        issued_at = int(timestamp)
        if abs(time.time() - issued_at) > 300:
            return False
        key_bytes = base64.b64decode(public_key, validate=True)
        signature_bytes = base64.b64decode(signature, validate=True)
        key = Ed25519PublicKey.from_public_bytes(key_bytes)
        key.verify(signature_bytes, timestamp.encode("ascii") + b"|" + body)
        return True
    except (ValueError, binascii.Error, UnicodeEncodeError, InvalidSignature):
        return False


async def telnyx_call_command(api_key: str, call_control_id: str, action: str, data: dict[str, str]) -> None:
    async with httpx.AsyncClient(timeout=httpx.Timeout(10, connect=3)) as client:
        response = await client.post(
            f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/{action}",
            headers={"Authorization": f"Bearer {api_key}"},
            json=data,
        )
    if response.is_error:
        logger.error("Telnyx call command failed: action=%s status=%s", action, response.status_code)
        raise HTTPException(status_code=502, detail="Telnyx call command failed")


@app.post("/telnyx/webhook")
async def telnyx_webhook(request: Request) -> JSONResponse:
    public_key = getattr(request.app.state, "telnyx_public_key", "")
    signature = request.headers.get("telnyx-signature-ed25519", "")
    timestamp = request.headers.get("telnyx-timestamp", "")
    if not public_key or not signature or not timestamp:
        raise HTTPException(status_code=403, detail="Missing Telnyx webhook verification configuration")

    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_WEBHOOK_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large")
    body = await request.body()
    if len(body) > MAX_WEBHOOK_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large")
    if not verify_telnyx_signature(body, signature, timestamp, public_key):
        raise HTTPException(status_code=403, detail="Invalid Telnyx webhook signature")
    try:
        envelope = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid JSON") from None

    data = envelope.get("data", {}) if isinstance(envelope, dict) else {}
    payload = data.get("payload", {}) if isinstance(data, dict) else {}
    event_type = data.get("event_type") if isinstance(data, dict) else None
    if not isinstance(payload, dict):
        return JSONResponse({"ok": True, "ignored": True})
    call_control_id = payload.get("call_control_id")
    if not isinstance(call_control_id, str) or not re.fullmatch(r"[A-Za-z0-9:_-]{1,200}", call_control_id):
        return JSONResponse({"ok": True, "ignored": True})

    api_key = getattr(request.app.state, "telnyx_api_key", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="Telnyx API key is not configured")
    event_id = data.get("id") if isinstance(data, dict) else None
    command_id = event_id if isinstance(event_id, str) and event_id else str(uuid4())
    client_state = base64.b64encode(b"saba-telnyx-v1").decode("ascii")

    if event_type == "call.initiated" and payload.get("direction") == "incoming":
        await telnyx_call_command(
            api_key,
            call_control_id,
            "answer",
            {"command_id": command_id, "client_state": client_state},
        )
    elif event_type == "call.answered" and payload.get("client_state") == client_state:
        await telnyx_call_command(
            api_key,
            call_control_id,
            "speak",
            {
                "command_id": command_id,
                "client_state": client_state,
                "payload_type": "text",
                "service_level": "basic",
                "voice": "female",
                "language": "en-US",
                "payload": (
                    "Thank you for calling Saba ET. The Telnyx connection is working, "
                    "but interactive voice assistance is not configured yet. Please use "
                    "the Saba Telegram assistant. Goodbye."
                ),
            },
        )
    elif event_type == "call.speak.ended" and payload.get("client_state") == client_state:
        await telnyx_call_command(api_key, call_control_id, "hangup", {"command_id": command_id})

    return JSONResponse({"ok": True})

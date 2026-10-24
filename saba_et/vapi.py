"""Opt-in Vapi outbound calls to source-verified, allowlisted public contacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit
from uuid import uuid4

import httpx
from saba_et.database import connect, database_url


@dataclass(frozen=True)
class VoiceContact:
    id: str
    name: str
    number: str
    source_url: str
    search_terms: tuple[str, ...]
    enabled: bool

    @classmethod
    def from_json(cls, item: object) -> "VoiceContact":
        if not isinstance(item, dict):
            raise ValueError("Voice contacts must be JSON objects.")
        contact_id = str(item.get("id", "")).strip()
        name = str(item.get("name", "")).strip()
        number = str(item.get("number", "")).strip()
        source_url = str(item.get("source_url", "")).strip()
        terms_value = item.get("search_terms", [])
        if not re.fullmatch(r"[a-z0-9_-]{1,40}", contact_id):
            raise ValueError("Each voice contact needs a lowercase id using letters, numbers, '_' or '-'.")
        if not name or len(name) > 100:
            raise ValueError("Each voice contact needs a name of at most 100 characters.")
        if not re.fullmatch(r"\+251[0-9]{9}", number):
            raise ValueError(f"Voice contact {contact_id!r} must use a valid-format Ethiopian +251 phone number.")
        parsed = urlsplit(source_url)
        host = (parsed.hostname or "").lower().rstrip(".")
        official = (
            host == "gov.et" or host.endswith(".gov.et")
            or host == "eaes.et" or host.endswith(".eaes.et")
            or host == "ebc.et" or host.endswith(".ebc.et")
        )
        if parsed.scheme != "https" or not official:
            raise ValueError(f"Voice contact {contact_id!r} needs an HTTPS Ethiopian public-service source URL.")
        if not isinstance(terms_value, list) or not terms_value:
            raise ValueError(f"Voice contact {contact_id!r} needs at least one search term.")
        terms = tuple(str(term).casefold().strip() for term in terms_value if str(term).strip())
        return cls(contact_id, name, number, source_url, terms, item.get("enabled") is True)

    def matches(self, question: str) -> bool:
        normalized = question.casefold()
        return any(term in normalized for term in self.search_terms)


@dataclass(frozen=True)
class VapiSettings:
    enabled: bool
    api_key: str
    assistant_id: str
    phone_number_id: str
    webhook_secret: str
    max_calls_per_day: int

    @classmethod
    def from_env(cls) -> "VapiSettings":
        enabled = os.environ.get("VAPI_AUTO_CALL_ENABLED", "false").strip().casefold() in {"1", "true", "yes"}
        raw_limit = os.environ.get("VAPI_MAX_CALLS_PER_DAY", "3").strip()
        try:
            daily_limit = int(raw_limit)
        except ValueError:
            daily_limit = 3
        daily_limit = min(max(daily_limit, 1), 20)
        return cls(
            enabled=enabled,
            api_key=os.environ.get("VAPI_API_KEY", "").strip(),
            assistant_id=os.environ.get("VAPI_ASSISTANT_ID", "").strip(),
            phone_number_id=os.environ.get("VAPI_PHONE_NUMBER_ID", "").strip(),
            webhook_secret=os.environ.get("VAPI_WEBHOOK_SECRET", "").strip(),
            max_calls_per_day=daily_limit,
        )

    @property
    def ready(self) -> bool:
        return self.enabled and self.configured

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.assistant_id and self.phone_number_id and self.webhook_secret)


def load_voice_contacts(path: Path) -> list[VoiceContact]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Voice contacts file must contain a JSON array.")
    contacts = [VoiceContact.from_json(item) for item in raw]
    ids = [item.id for item in contacts]
    if len(set(ids)) != len(ids):
        raise ValueError("Voice contact ids must be unique.")
    return contacts


class VapiCallLedger:
    """Persist only call routing metadata; never store transcripts or recordings."""

    def __init__(self, database_path: Path) -> None:
        self._path = database_path
        self._postgres = bool(database_url())
        if self._postgres:
            return
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS vapi_calls (
                    reservation_id TEXT PRIMARY KEY,
                    call_id TEXT UNIQUE,
                    user_id TEXT NOT NULL,
                    contact_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL
                )"""
            )

    def reserve(self, user_id: int, contact_id: str, daily_limit: int) -> str | None:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        reservation_id = uuid4().hex
        if self._postgres:
            with connect() as connection:
                with connection.transaction():
                    connection.execute("SELECT pg_advisory_xact_lock(71234, %s)", (int(now.strftime("%Y%m%d")),))
                    count = connection.execute("""SELECT COUNT(*) AS count FROM vapi_calls
                        WHERE created_at >= %s AND status IN ('reserved','started','completed')""", (now.replace(hour=0, minute=0, second=0, microsecond=0),)).fetchone()["count"]
                    if count >= daily_limit:
                        return None
                    connection.execute("INSERT INTO vapi_calls (reservation_id, user_id, contact_id, created_at, status) VALUES (%s,%s,%s,%s,'reserved')",
                        (reservation_id, str(user_id), contact_id, now))
            return reservation_id
        with sqlite3.connect(self._path, timeout=10) as connection:
            connection.execute("BEGIN IMMEDIATE")
            count = connection.execute(
                "SELECT COUNT(*) FROM vapi_calls WHERE created_at >= ? AND status IN ('reserved', 'started', 'completed')",
                (start_of_day,),
            ).fetchone()[0]
            if count >= daily_limit:
                return None
            connection.execute(
                "INSERT INTO vapi_calls (reservation_id, user_id, contact_id, created_at, status) VALUES (?, ?, ?, ?, 'reserved')",
                (reservation_id, str(user_id), contact_id, now.isoformat()),
            )
        return reservation_id

    def mark_started(self, reservation_id: str, call_id: str) -> None:
        if self._postgres:
            with connect() as connection:
                connection.execute("UPDATE vapi_calls SET call_id=%s, status='started' WHERE reservation_id=%s", (call_id, reservation_id))
            return
        with sqlite3.connect(self._path, timeout=10) as connection:
            connection.execute(
                "UPDATE vapi_calls SET call_id = ?, status = 'started' WHERE reservation_id = ?",
                (call_id, reservation_id),
            )

    def mark_failed(self, reservation_id: str) -> None:
        if self._postgres:
            with connect() as connection:
                connection.execute("UPDATE vapi_calls SET status='failed' WHERE reservation_id=%s", (reservation_id,))
            return
        with sqlite3.connect(self._path, timeout=10) as connection:
            connection.execute(
                "UPDATE vapi_calls SET status = 'failed' WHERE reservation_id = ?",
                (reservation_id,),
            )

    def finish(self, call_id: str) -> int | None:
        if self._postgres:
            with connect() as connection:
                with connection.transaction():
                    row = connection.execute("SELECT user_id, status FROM vapi_calls WHERE call_id=%s FOR UPDATE", (call_id,)).fetchone()
                    if not row or row["status"] != "started":
                        return None
                    connection.execute("UPDATE vapi_calls SET status='completed' WHERE call_id=%s", (call_id,))
                    return int(row["user_id"])
        with sqlite3.connect(self._path, timeout=10) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT user_id, status FROM vapi_calls WHERE call_id = ?",
                (call_id,),
            ).fetchone()
            if not row or row[1] != "started":
                return None
            connection.execute("UPDATE vapi_calls SET status = 'completed' WHERE call_id = ?", (call_id,))
        return int(row[0])


class VapiClient:
    def __init__(self, settings: VapiSettings) -> None:
        self._settings = settings

    async def create_call(
        self,
        contact: VoiceContact,
        purpose: str,
        question: str,
        language: str,
        user_id: int,
    ) -> str:
        payload = {
            "assistantId": self._settings.assistant_id,
            "phoneNumberId": self._settings.phone_number_id,
            "customer": {"number": contact.number, "name": contact.name},
            "assistantOverrides": {
                "variableValues": {
                    "office_name": contact.name,
                    "call_purpose": purpose[:240],
                    "question_to_ask": question[:400],
                    "call_language": language,
                }
            },
            "metadata": {"saba_user_id": str(user_id), "saba_contact_id": contact.id},
        }
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(15, connect=5)) as session:
                response = await session.post(
                    "https://api.vapi.ai/call",
                    headers={"Authorization": f"Bearer {self._settings.api_key}"},
                    json=payload,
                )
            response.raise_for_status()
            result = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RuntimeError(type(exc).__name__) from None
        call_id = result.get("id") if isinstance(result, dict) else None
        if not isinstance(call_id, str) or not call_id:
            raise RuntimeError("invalid_response")
        return call_id

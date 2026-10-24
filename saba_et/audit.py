"""Minimal local audit trail that never stores message contents."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from saba_et.database import connect, database_url


class AuditLog:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._postgres = bool(database_url())
        if self._postgres:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY,
                    occurred_at TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    consent TEXT NOT NULL
                )"""
            )

    def record(self, actor_id: int, action: str, consent: bool) -> None:
        """Store event metadata only; never pass user message text here."""
        if self._postgres:
            with connect() as connection:
                connection.execute("INSERT INTO audit_events (occurred_at, actor_id, action, consent) VALUES (%s, %s, %s, %s)",
                    (datetime.now(timezone.utc), str(actor_id), action, consent))
            return
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                "INSERT INTO audit_events (occurred_at, actor_id, action, consent) VALUES (?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    str(actor_id),
                    action,
                    "yes" if consent else "no",
                ),
            )

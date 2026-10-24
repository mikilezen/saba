"""Durable, deduplicated Telegram webhook inbox backed by Supabase Postgres."""

from __future__ import annotations

import json
from saba_et.database import connect


class TelegramJobQueue:
    def enqueue(self, update: dict) -> bool:
        with connect() as connection:
            cursor = connection.execute("""INSERT INTO telegram_jobs (update_id, payload)
                VALUES (%s, %s::jsonb) ON CONFLICT (update_id) DO NOTHING""",
                (update["update_id"], json.dumps(update, ensure_ascii=False)))
            return cursor.rowcount == 1

    def claim(self) -> dict | None:
        with connect() as connection:
            with connection.transaction():
                # Expire abandoned payloads after process crashes; never replay
                # an event whose side effects are uncertain.
                connection.execute("DELETE FROM telegram_jobs WHERE status='processing' AND claimed_at < now() - interval '10 minutes'")
                row = connection.execute("""SELECT id, payload FROM telegram_jobs
                    WHERE status='queued'
                    ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED""").fetchone()
                if not row:
                    return None
                connection.execute("UPDATE telegram_jobs SET status='processing', claimed_at=now(), attempts=attempts+1 WHERE id=%s", (row["id"],))
                payload = row["payload"]
                if isinstance(payload, str):
                    payload = json.loads(payload)
                return {"id": row["id"], "payload": payload}

    def finish(self, job_id: int) -> None:
        with connect() as connection:
            # Do not replay a handled event automatically: it may already have
            # triggered external work before the response failed.
            connection.execute("DELETE FROM telegram_jobs WHERE id=%s", (job_id,))

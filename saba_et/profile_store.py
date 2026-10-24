"""Local, consent-gated preferences and optional user profile fields."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from saba_et.database import connect, database_url


class ProfileStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._postgres = bool(database_url())
        if self._postgres:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    language TEXT NOT NULL DEFAULT 'en',
                    personal_data_consent INTEGER NOT NULL DEFAULT 0,
                    contact_name TEXT,
                    age TEXT,
                    birth_year TEXT,
                    location TEXT,
                    updated_at TEXT NOT NULL
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS conversation_state (
                    user_id TEXT PRIMARY KEY,
                    stage TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS application_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )"""
            )

    def is_configured(self, key: str) -> bool:
        if self._postgres:
            with connect() as connection:
                row = connection.execute("SELECT value FROM application_settings WHERE key = %s", (key,)).fetchone()
            return bool(row and row["value"] == "1")
        with sqlite3.connect(self._path) as connection:
            row = connection.execute(
                "SELECT value FROM application_settings WHERE key = ?",
                (key,),
            ).fetchone()
        return bool(row and row[0] == "1")

    def mark_configured(self, key: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if self._postgres:
            with connect() as connection:
                connection.execute("""INSERT INTO application_settings (key, value, updated_at)
                    VALUES (%s, '1', %s) ON CONFLICT(key) DO UPDATE SET value='1', updated_at=EXCLUDED.updated_at""", (key, now))
            return
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """INSERT INTO application_settings (key, value, updated_at)
                   VALUES (?, '1', ?) ON CONFLICT(key) DO UPDATE SET
                   value = '1', updated_at = excluded.updated_at""",
                (key, now),
            )

    def get_stage(self, user_id: int) -> str | None:
        if self._postgres:
            with connect() as connection:
                row = connection.execute("SELECT stage FROM conversation_state WHERE user_id = %s", (str(user_id),)).fetchone()
            return str(row["stage"]) if row else None
        with sqlite3.connect(self._path) as connection:
            row = connection.execute(
                "SELECT stage FROM conversation_state WHERE user_id = ?",
                (str(user_id),),
            ).fetchone()
        return str(row[0]) if row else None

    def save_stage(self, user_id: int, stage: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if self._postgres:
            with connect() as connection:
                connection.execute("""INSERT INTO conversation_state (user_id, stage, updated_at)
                    VALUES (%s, %s, %s) ON CONFLICT(user_id) DO UPDATE SET stage=EXCLUDED.stage, updated_at=EXCLUDED.updated_at""", (str(user_id), stage, now))
            return
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """INSERT INTO conversation_state (user_id, stage, updated_at)
                   VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET
                   stage = excluded.stage, updated_at = excluded.updated_at""",
                (str(user_id), stage, now),
            )

    def get(self, user_id: int) -> dict[str, str | bool | None] | None:
        if self._postgres:
            with connect() as connection:
                row = connection.execute("""SELECT language, personal_data_consent, contact_name, age, birth_year, location
                    FROM user_profiles WHERE user_id = %s""", (str(user_id),)).fetchone()
            if row is None:
                return None
            return {"language": row["language"], "personal_data_consent": row["personal_data_consent"],
                    "name": row["contact_name"], "age": row["age"], "birth_year": row["birth_year"], "location": row["location"]}
        with sqlite3.connect(self._path) as connection:
            row = connection.execute(
                "SELECT language, personal_data_consent, contact_name, age, birth_year, location "
                "FROM user_profiles WHERE user_id = ?",
                (str(user_id),),
            ).fetchone()
        if row is None:
            return None
        return {
            "language": row[0],
            "personal_data_consent": bool(row[1]),
            "name": row[2],
            "age": row[3],
            "birth_year": row[4],
            "location": row[5],
        }

    def save_language(self, user_id: int, language: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if self._postgres:
            with connect() as connection:
                connection.execute("""INSERT INTO user_profiles (user_id, language, updated_at) VALUES (%s, %s, %s)
                    ON CONFLICT(user_id) DO UPDATE SET language=EXCLUDED.language, updated_at=EXCLUDED.updated_at""", (str(user_id), language, now))
            return
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """INSERT INTO user_profiles (user_id, language, updated_at) VALUES (?, ?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET language = excluded.language,
                   updated_at = excluded.updated_at""",
                (str(user_id), language, now),
            )

    def grant_personal_data_consent(self, user_id: int, language: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if self._postgres:
            with connect() as connection:
                connection.execute("""INSERT INTO user_profiles (user_id, language, personal_data_consent, updated_at)
                    VALUES (%s, %s, TRUE, %s) ON CONFLICT(user_id) DO UPDATE SET language=EXCLUDED.language,
                    personal_data_consent=TRUE, updated_at=EXCLUDED.updated_at""", (str(user_id), language, now))
            return
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """INSERT INTO user_profiles (user_id, language, personal_data_consent, updated_at)
                   VALUES (?, ?, 1, ?)
                   ON CONFLICT(user_id) DO UPDATE SET language = excluded.language,
                   personal_data_consent = 1, updated_at = excluded.updated_at""",
                (str(user_id), language, now),
            )

    def save_personal_fields(self, user_id: int, language: str, values: dict[str, str]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if self._postgres:
            with connect() as connection:
                connection.execute("""UPDATE user_profiles SET language=%s, contact_name=%s, age=%s,
                    birth_year=%s, location=%s, updated_at=%s WHERE user_id=%s AND personal_data_consent=TRUE""",
                    (language, values.get("name"), values.get("age"), values.get("birth_year"), values.get("location"), now, str(user_id)))
            return
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """UPDATE user_profiles SET language = ?, contact_name = ?, age = ?,
                   birth_year = ?, location = ?, updated_at = ?
                   WHERE user_id = ? AND personal_data_consent = 1""",
                (
                    language,
                    values.get("name"),
                    values.get("age"),
                    values.get("birth_year"),
                    values.get("location"),
                    now,
                    str(user_id),
                ),
            )

    def forget_personal_data(self, user_id: int) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if self._postgres:
            with connect() as connection:
                connection.execute("""UPDATE user_profiles SET personal_data_consent=FALSE, contact_name=NULL,
                    age=NULL, birth_year=NULL, location=NULL, updated_at=%s WHERE user_id=%s""", (now, str(user_id)))
            return
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """UPDATE user_profiles SET personal_data_consent = 0, contact_name = NULL,
                   age = NULL, birth_year = NULL, location = NULL, updated_at = ?
                   WHERE user_id = ?""",
                (now, str(user_id)),
            )

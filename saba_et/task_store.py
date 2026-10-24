"""Persistent, actor-scoped goals used to resume multi-step work."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from uuid import UUID

from saba_et.database import connect, database_url


FINAL_STATUSES = {"completed", "failed", "cancelled"}


class TaskStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._postgres = bool(database_url())
        if self._postgres:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._path) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("""CREATE TABLE IF NOT EXISTS goal_tasks (
                task_id TEXT PRIMARY KEY, actor_id TEXT NOT NULL, channel TEXT NOT NULL,
                goal TEXT NOT NULL, objective TEXT NOT NULL, service_id TEXT,
                status TEXT NOT NULL, current_step TEXT, next_action TEXT,
                subtasks TEXT NOT NULL DEFAULT '[]', constraints TEXT NOT NULL DEFAULT '[]',
                permissions TEXT NOT NULL DEFAULT '{}', deadline TEXT, completion_criteria TEXT,
                created_at TEXT NOT NULL, last_activity TEXT NOT NULL, completed_at TEXT)""")
            connection.execute("CREATE INDEX IF NOT EXISTS goal_tasks_actor_open_idx ON goal_tasks(actor_id, last_activity)")

    @staticmethod
    def _decode(row: dict | sqlite3.Row | None) -> dict | None:
        if row is None:
            return None
        data = dict(row)
        for key in ("subtasks", "constraints", "permissions"):
            value = data.get(key)
            if isinstance(value, str):
                data[key] = json.loads(value)
        return data

    def create(self, actor_id: int, channel: str, goal: str, objective: str) -> dict:
        task_id = str(uuid4())
        now = datetime.now(timezone.utc)
        subtask_rows = [{"name": "clarify_scope", "status": "pending"}, {"name": "plan_safe_next_step", "status": "pending"}]
        permissions = {"read_public": True, "login": False, "fill": False, "upload": False, "pay": False, "submit": False}
        if self._postgres:
            with connect() as connection:
                row = connection.execute("""INSERT INTO goal_tasks
                    (task_id, actor_id, channel, goal, objective, status, current_step, next_action,
                     subtasks, constraints, permissions, completion_criteria, created_at, last_activity)
                    VALUES (%s::uuid, %s, %s, %s, %s, 'pending', 'clarify_scope',
                     'Confirm service and requirements before acting', %s::jsonb, '[]'::jsonb,
                     %s::jsonb, 'Record a verified outcome or hand off to the responsible office', %s, %s)
                    RETURNING *""", (task_id, str(actor_id), channel, goal, objective,
                                      json.dumps(subtask_rows), json.dumps(permissions), now, now)).fetchone()
            return self._decode(row) or {}
        now_text = now.isoformat()
        with sqlite3.connect(self._path) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("""INSERT INTO goal_tasks
                (task_id, actor_id, channel, goal, objective, status, current_step, next_action,
                 subtasks, constraints, permissions, completion_criteria, created_at, last_activity)
                VALUES (?, ?, ?, ?, ?, 'pending', 'clarify_scope',
                 'Confirm service and requirements before acting', ?, '[]', ?,
                 'Record a verified outcome or hand off to the responsible office', ?, ?)""",
                (task_id, str(actor_id), channel, goal, objective, json.dumps(subtask_rows),
                 json.dumps(permissions), now_text, now_text))
            return self._decode(connection.execute("SELECT * FROM goal_tasks WHERE task_id=?", (task_id,)).fetchone()) or {}

    def list_open(self, actor_id: int, limit: int = 10) -> list[dict]:
        if self._postgres:
            with connect() as connection:
                rows = connection.execute("""SELECT * FROM goal_tasks WHERE actor_id=%s
                    AND status NOT IN ('completed','failed','cancelled') ORDER BY last_activity DESC LIMIT %s""",
                    (str(actor_id), limit)).fetchall()
            return [self._decode(row) or {} for row in rows]
        with sqlite3.connect(self._path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute("""SELECT * FROM goal_tasks WHERE actor_id=?
                AND status NOT IN ('completed','failed','cancelled') ORDER BY last_activity DESC LIMIT ?""",
                (str(actor_id), limit)).fetchall()
        return [self._decode(row) or {} for row in rows]

    def get(self, actor_id: int, task_id: str) -> dict | None:
        try:
            task_id = str(UUID(task_id))
        except (ValueError, TypeError, AttributeError):
            return None
        if self._postgres:
            with connect() as connection:
                row = connection.execute("SELECT * FROM goal_tasks WHERE task_id=%s::uuid AND actor_id=%s",
                                         (task_id, str(actor_id))).fetchone()
            return self._decode(row)
        with sqlite3.connect(self._path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute("SELECT * FROM goal_tasks WHERE task_id=? AND actor_id=?", (task_id, str(actor_id))).fetchone()
        return self._decode(row)

    def set_status(self, actor_id: int, task_id: str, status: str) -> dict | None:
        if status not in {"paused", "pending"}:
            raise ValueError("Only pause and resume transitions are allowed here.")
        task = self.get(actor_id, task_id)
        if task is None or task["status"] in FINAL_STATUSES:
            return None
        if status == "paused" and task["status"] == "paused":
            return task
        if status == "pending" and task["status"] != "paused":
            return None
        now = datetime.now(timezone.utc)
        next_action = "Wait for the person to resume this task" if status == "paused" else "Confirm service and requirements before acting"
        if self._postgres:
            with connect() as connection:
                row = connection.execute("""UPDATE goal_tasks SET status=%s, next_action=%s, last_activity=%s
                    WHERE task_id=%s::uuid AND actor_id=%s RETURNING *""",
                    (status, next_action, now, task_id, str(actor_id))).fetchone()
            return self._decode(row)
        with sqlite3.connect(self._path) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("UPDATE goal_tasks SET status=?, next_action=?, last_activity=? WHERE task_id=? AND actor_id=?",
                               (status, next_action, now.isoformat(), task_id, str(actor_id)))
            row = connection.execute("SELECT * FROM goal_tasks WHERE task_id=? AND actor_id=?", (task_id, str(actor_id))).fetchone()
        return self._decode(row)

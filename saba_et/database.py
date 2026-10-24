"""Small Postgres connection helper for Supabase's direct database endpoint."""

from __future__ import annotations

import os

import psycopg
from psycopg.rows import dict_row


def database_url() -> str:
    return os.environ.get("SUPABASE_DB_URL", "").strip()


def connect():
    url = database_url()
    if not url:
        raise RuntimeError("SUPABASE_DB_URL is not configured.")
    return psycopg.connect(url, row_factory=dict_row, connect_timeout=8)

# Supabase setup

Saba uses Supabase Postgres for consented profiles, onboarding state, metadata-only audit events, Vapi call routing metadata, and a durable, deduplicated Telegram webhook inbox. The browser never connects to Supabase. Keep the database password in the backend environment only.

## Create and connect

1. Create a Supabase project and copy a PostgreSQL connection string from **Project Settings → Database → Connection string**. For serverless hosting, choose the session or transaction pooler URI recommended by Supabase; URL-encode special characters in the password.
2. In the Supabase SQL Editor, run [`supabase/migrations/202610030001_initial.sql`](../supabase/migrations/202610030001_initial.sql).
3. Set `SUPABASE_DB_URL` to the server-side connection URI in Render's secret environment settings. For local development, put it in the ignored `.env` file. Leave it blank to use local SQLite.
4. Deploy and confirm the service starts and `/healthz` responds. The webhook only acknowledges an update after Postgres accepts it.

The service connects as the project database owner using a server-only secret. Do not use an anon or public key as the database password, and do not expose `SUPABASE_DB_URL` to a frontend. RLS is enabled and browser roles have no table grants. The backend's database owner credential is privileged and must remain in secret storage.

## Data behavior

- Profile fields are written only after the existing consent flow; `/forget` clears the personal fields while preserving language.
- Telegram updates are deduplicated by `update_id`, queued in Postgres, and deleted after an attempt so message bodies are not retained as a history. An update whose handler fails is not automatically replayed, because the handler may already have performed work before a response failed. A processing payload left by a crashed process expires after ten minutes and is discarded rather than replayed.
- `/task create <goal>`, `/tasks`, `/task <id>`, `/task pause <id>`, and `/task resume <id>` now create and manage actor-scoped persistent goal records with safe default permissions. This is task tracking only: browser operations, approval-bound irreversible actions, scheduled tracking, and evidence-backed completion are not implemented. Do not enable irreversible actions based on the presence of these records.
- Existing local SQLite records are not automatically copied to Supabase. Keep a protected backup and perform a deliberate, consent-aware migration if preserving existing profiles is required.
- Apply schema changes through versioned SQL migrations. Supabase's free project may pause after inactivity; use a production plan and backups appropriate to the data and uptime requirement.

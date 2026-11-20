# Supabase migrations

This directory contains the database migrations for Saba's server-side data
store and durable Telegram inbox.

## Initial schema

[`202610030001_initial.sql`](202610030001_initial.sql) creates:

- User profiles, conversation state, and application settings
- Audit events and Vapi call reservations
- Durable goal tasks and task intents
- Queued Telegram jobs

The migration enables row-level security on every table and revokes browser
access from `anon` and `authenticated`. The trusted backend must use the
private database connection; never expose its database password or service
credentials to a browser or client.

Apply migrations with the repository's Supabase workflow and review schema
changes before deploying them to a shared project.

# Ethiopian integrations

The `saba_et` package provides Ethiopia-focused service discovery and
conversation workflows.

- `application.py` coordinates consent-based, language-aware conversations.
- `domain.py` defines shared service and message models.
- `provider_directory.py` searches curated Ethiopian public-service providers.
- `knowledge.py` and `searchapi.py` support service knowledge and source lookup.
- `telegram/`, `telegram_jobs.py`, `vapi.py`, and `web.py` expose channel
  integrations.
- `audit.py`, `permissions.py`, and `profile_store.py` keep sensitive actions
  explicit and locally controlled.

Supported user-facing languages include English, Amharic, Afaan Oromoo, and
Tigrinya. Treat provider links as read-only references unless a fresh,
explicit user approval is required for an action.

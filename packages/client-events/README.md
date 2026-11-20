# Client events

This package contains shared TypeScript contracts and helpers for browser and
terminal clients.

- [`attachments.ts`](attachments.ts) validates local attachments and manages
  pasted-file references and uploads.
- [`delivery.ts`](delivery.ts) waits for message-acceptance receipts and keeps
  drafts safe when delivery is not confirmed.
- [`notifications.ts`](notifications.ts) defines and decodes retry, recovery,
  and context-compaction notifications.
- [`fixtures.json`](fixtures.json) contains representative notification
  payloads for tests and development.

Keep event names and payload fields backward-compatible across client and
gateway releases.

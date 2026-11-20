# Saba Coding Agent Instructions

Use the agent name **Saba Coding Agent** in repository documentation and automated agent metadata.

Saba's Python gateway owns agent execution, sessions, tools, memory, provider integration, and security policy. WebUI and TUI are presentation and transport clients; do not move gateway policy or runtime state into either client.

## Before changing code

- Read the relevant project and component guidance before implementation.
- Analyze the observable behavior, ownership boundaries, root cause, and affected contracts.
- Preserve existing public behavior unless the request intentionally changes it.
- Prefer the smallest complete fix over speculative fallbacks or broad rewrites.
- Reuse established helpers, models, test fixtures, and patterns.
- Do not add tests for impossible, unsupported, or nonexistent states.
- Do not create a commit unless the user explicitly asks for one.

## Required guidance

| Area | Read |
| --- | --- |
| Ownership, abstractions, and dynamic types | [`.agent/design.md`](.agent/design.md) |
| Simplification and verification evidence | [`.agent/simplify.md`](.agent/simplify.md), [`.agent/workflow.md`](.agent/workflow.md) |
| User-facing copy and localization | [`.agent/copywriting.md`](.agent/copywriting.md) |
| Security, permissions, and isolation | [`.agent/security.md`](.agent/security.md) |
| Setup, Windows, configuration, prompts, and persistence | [`.agent/gotchas.md`](.agent/gotchas.md) |
| WebUI-host compatibility | [`.agent/review-guide.md`](.agent/review-guide.md) |

## Engineering rules

- Keep execution, state ownership, security primitives, and persistence independent of API, channel, CLI, and WebUI adapters.
- Add capabilities through channels, tools, skills, or external MCP integrations when they fit there; keep the core loop small.
- Type wire payloads, persisted records, and third-party SDK objects at their boundaries.
- Preserve backward compatibility for protocol fields, session data, and persisted configuration.
- Keep secrets in local environment variables or deployment secret managers. Never print, commit, or add real credentials to examples.
- Keep official-source claims, consent gates, and sensitive-action approvals explicit.
- Do not silently install, restart, revoke credentials, downgrade, or reset configuration.

## Verification

- Run the smallest test or check that covers the changed contract.
- Rerun verification only when assumptions or dependencies change.
- Use existing lint, type-check, build, and test commands.
- Report failures, skipped checks, and inherited evidence clearly.
- Never present planned support or fixture-only behavior as a completed real-world acceptance test.
- Keep raw verification artifacts outside tracked source files.

## Repository formatting

- Follow existing file and naming conventions.
- Do not run `ruff format`; it can create unrelated diffs and obscures git blame.
- Do not manually wrap Markdown prose. Keep paragraphs on one source line; use line breaks only for Markdown structure.
- Preserve existing behavior and avoid unrelated cleanup.

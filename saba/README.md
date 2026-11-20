# Saba agent package

The `saba` package contains the agent runtime, providers, tools, channels,
session handling, and application integrations.

## Runtime guidance

- Keep the agent loop and runner focused on orchestration; place integrations
  at the relevant channel, tool, or provider boundary.
- Preserve typed contracts at protocol and persistence boundaries.
- Initial messages must be prepared through the runner's context-compaction
  path so an oversized first request can be reduced before it reaches a model.
- Keep user-visible failures explicit and preserve drafts or state when delivery
  or recovery cannot be confirmed.

See the package's subdirectories for component-specific implementation and
testing guidance.

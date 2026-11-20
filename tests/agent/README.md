# Agent test coverage

This directory contains focused tests for the agent runtime and its supporting
components.

For oversized initial messages, review the tests covering:

- Runner prompt preparation and initial-message handling
- Context consolidation and token pressure
- Error and fallback behavior when a request cannot fit
- Persistence of the original context and the resulting compaction state

Keep regression cases at the narrowest relevant layer, then run the targeted
agent test module before the broader agent suite.

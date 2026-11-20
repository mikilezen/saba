# Agent skill definitions

This directory contains reusable agent skills. Each skill lives in its own
directory and is defined by a `SKILL.md` file.

## Available skills

- [`gemini-api-dev`](gemini-api-dev/SKILL.md) - Gemini API development
- [`supabase`](supabase/SKILL.md) - Supabase products, integrations, and operations
- [`supabase-postgres-best-practices`](supabase-postgres-best-practices/SKILL.md) - PostgreSQL schema, performance, and security practices
- [`typesafe-ai`](typesafe-ai/SKILL.md) - TypeSafe AI application patterns

## Definition format

Each `SKILL.md` starts with YAML front matter containing:

- `name`: the skill identifier, matching its directory name
- `description`: when the agent should load the skill

Keep the description specific enough to trigger the skill for relevant tasks,
and keep detailed instructions and references in the body of `SKILL.md`.

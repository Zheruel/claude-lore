# Architecture

Run `/lore-init` to scan your projects and generate architecture documentation.

## Skills

- `/lore-init` - Scan all projects and generate full system documentation
- `/lore-update` - Update docs after code changes
- `/lore-ticket [description]` - Create implementation tickets for features or tasks

## What Happens After Init

This file transforms into a comprehensive system overview containing:
- All detected projects with their tech stacks
- How projects connect to each other
- Key file locations for each project
- Patterns and conventions used
- Step-by-step guides for building new features

The generated documentation lives in:
- `OVERVIEW.md` - System architecture with diagrams
- `services/` - Per-project detailed documentation
- `tickets/` - Implementation plans

## Ticket Guidelines

Tickets are designed as input for Claude Code **plan mode**. When creating tickets:
- Never include code snippets — explain **what** to do and **why**
- Focus on architectural decisions and their rationale
- Reference specific file paths that need modification
- For frontend work, note to use the `/frontend-design` skill during implementation
- Include edge cases, integration points, and testing strategy
- Keep it clear and concise

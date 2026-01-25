# Architecture

Run `/lore-init` to scan your projects and generate architecture documentation.

## Commands

- `/lore-init` - Scan all projects and generate full system documentation
- `/lore-update` - Update docs after code changes

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
- `tickets/` - Implementation plans you create

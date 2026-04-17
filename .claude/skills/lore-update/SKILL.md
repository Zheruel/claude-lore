---
name: lore-update
description: Re-scan the codebase and regenerate the lean CLAUDE.md architecture index
disable-model-invocation: true
---

# Lore Update

Re-scan the codebase and regenerate the `CLAUDE.md` architecture index to reflect the current state.

## Goal

Idempotent rewrite. Re-run discovery, re-explore each project, and rewrite `CLAUDE.md` in place. No diffing of stale files, no partial updates — the cost of a full rewrite is small and the cost of stale partials is high.

## Procedure

1. **Re-discover projects.** Same project markers and skip rules as `lore-init`. Compare against the projects table in the current `CLAUDE.md` to know what's new, removed, or unchanged.

2. **Re-explore in parallel.** Launch Explore agents (`subagent_type: Explore`) for every discovered project — not just the changed ones. The whole point of this skill is that the index reflects *current* reality, so re-exploring everything is the safe default and the cost is bounded by parallelism.

3. **Detect external services and cross-project edges.** Same logic as `lore-init`: API/RPC calls, shared types, shared databases, queues, auth flows, shared env vars.

4. **Rewrite `CLAUDE.md`.** Follow the structure defined in the `lore-init` skill (`.claude/skills/lore-init/SKILL.md`) exactly. Lean index, projects table, external services table, cross-project Mermaid diagram, key locations per project, patterns & conventions, ticket pointer. Nothing more.

Do not touch `tickets/[feature].md` files — those are user-created and stay.

## Consistency check

Before finishing:

- `CLAUDE.md` exists at the architecture root
- Every project path actually points to a real folder

## Summary

Report:

- Projects scanned (count)
- New projects since last run, if any
- Removed projects since last run, if any
- New cross-project edges or external services worth flagging
- Index regenerated: `CLAUDE.md`

---

Now re-scan and regenerate.

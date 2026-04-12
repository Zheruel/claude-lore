---
name: lore-update
description: Re-scan the codebase and regenerate the lean CLAUDE.md index plus the architecture.html report
disable-model-invocation: true
---

# Lore Update

Re-scan the codebase and regenerate both architecture artifacts to reflect the current state.

## Goal

Idempotent rewrite. Re-run discovery, re-explore each project, and rewrite both `CLAUDE.md` and `architecture.html` in place. No diffing of stale files, no partial updates — the cost of a full rewrite is small and the cost of stale partials is high.

Two artifacts only:

- **`CLAUDE.md`** — lean index for Claude
- **`architecture.html`** — rich human-facing report

## Procedure

1. **Re-discover projects.** Same project markers and skip rules as `lore-init`. Compare against the projects table in the current `CLAUDE.md` to know what's new, removed, or unchanged.

2. **Re-explore in parallel.** Launch Explore agents (`subagent_type: Explore`) for every discovered project — not just the changed ones. The whole point of this skill is that the artifacts reflect *current* reality, so re-exploring everything is the safe default and the cost is bounded by parallelism.

3. **Detect external services and cross-project edges.** Same logic as `lore-init`: API/RPC calls, shared types, shared databases, queues, auth flows, shared env vars.

4. **Rewrite `CLAUDE.md`.** Follow the structure defined in the `lore-init` skill (`.claude/skills/lore-init/SKILL.md`) exactly. Lean index, projects table, external services table, cross-project Mermaid diagram, key locations per project, patterns & conventions, ticket pointer. Nothing more.

5. **Rewrite `architecture.html`.** Same structure as `lore-init`: single self-contained HTML file at the architecture root, Mermaid via CDN, eight required sections (Overview · Projects · Architecture diagram · External services · Data flows · Per-project deep dives · Patterns & conventions · Building new features).

Do not touch `tickets/[feature].md` files — those are user-created and stay.

## Consistency check

Before finishing:

- `CLAUDE.md` and `architecture.html` both exist at the architecture root
- Project names and paths match between the two
- Every project path actually points to a real folder
- The Mermaid CDN script tag is present in `architecture.html`

## Summary

Report:

- Projects scanned (count)
- New projects since last run, if any
- Removed projects since last run, if any
- New cross-project edges or external services worth flagging
- Both artifacts regenerated: `CLAUDE.md`, `architecture.html`

---

Now re-scan and regenerate.

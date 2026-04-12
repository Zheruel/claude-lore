---
name: lore-ticket
description: Create an architectural implementation ticket for a feature or task that spans one or more services. Use when asked to create a ticket, plan, or implementation spec.
argument-hint: "feature description"
---

# Lore Ticket

Create an implementation ticket for: **$ARGUMENTS**

Ultrathink deeply about the architectural implications before writing anything. Consider the full system, not just the obvious touch points.

## Before Writing

1. **Read `CLAUDE.md`** — get the projects table, cross-project edges, and key locations. This is your map.
2. **Explore the actual code** — Launch Explore agents (`subagent_type: Explore`) for each project that might be affected. The code is the source of truth; `CLAUDE.md` is just an index into it. Always re-explore.
3. **Map the impact** — Identify every service, database, API, and integration point that this feature touches.

## Ticket Format

Write the ticket as a **clear architectural plan optimized for Claude Code plan mode**. This is the most important constraint: the ticket will be fed to Claude in plan mode to drive implementation.

### Rules

- **Never include code snippets** — explain what to do and why, not how to write it
- **Focus on architecture** — what changes where, why that approach, what are the tradeoffs
- **Be specific about files** — reference exact file paths that need modification
- **Frontend work** — if the ticket involves frontend/UI changes, note that the `/frontend-design` skill should be used during implementation
- **Keep it concise** — every sentence should add information. No filler, no preamble
- **Think cross-service** — trace the feature across all boundaries

### Example

See [example.md](example.md) for a calibration example of the quality, specificity, and conciseness expected.

### Structure

```markdown
# [Feature Title]

## Problem
[What problem does this solve? Why does it matter? 2-3 sentences max.]

## Approach
[High-level architectural strategy. What's the design decision and why?]

## Affected Services

| Service | Changes | Impact |
|---------|---------|--------|
| [name] | [what changes] | [high/medium/low] |

## Implementation Plan

### 1. [Service Name] — [What to do]
- **Why:** [Architectural reason for this change]
- **Where:** `path/to/relevant/files`
- **What:** [Description of the changes needed]
- **Watch out:** [Gotchas, constraints, things that could break]

### 2. [Next Service] — [What to do]
...

[Order the steps by dependency — what must be done first]

## Integration Points
[How do the changes across services connect? What contracts exist between them?]

## Edge Cases
[What could go wrong? What are the boundary conditions?]

## Testing Strategy
[What needs to be tested and at what level — unit, integration, e2e?]

## Notes
[Any additional context, links to external docs, or open questions]
```

## After Writing

Save the ticket at `tickets/[feature-name].md` (kebab-case). The ticket's `Affected Services` table is what tells you which repos it touches.

The intended execution workflow: the user pastes the *entire* ticket into Claude Code plan mode inside each affected service repo. Each repo's plan mode produces the per-service implementation plan with full local context. Write the ticket as a single shared brief that travels well across all affected services.

## Validation

After saving the ticket, use the Agent tool to launch the `ticket-validator` agent (defined in `.claude/agents/ticket-validator.md`), passing the saved ticket file path. Address any issues it flags.

## Summary

Report:
- Ticket saved to `[path]`
- Services affected
- Any architectural concerns or open questions worth discussing

---
name: lore-update
description: Update architecture documentation after code changes across the codebase
disable-model-invocation: true
---

# Lore Update

Update architecture documentation after code changes.

## Goal

Detect what changed across projects, re-explore only affected parts, and update documentation to reflect the current state.

## Detect Changes

Identify what needs updating:

- **New projects** — Folders with project markers not in current docs
- **Removed projects** — Documented projects whose folders no longer exist
- **Modified projects** — Check git status/diff in each project where available, or compare against existing `services/[project].md` docs
- **New external services** — New dependencies, environment variables, or integrations
- **Changed relationships** — New API calls, imports, shared types, or event patterns between projects

## Re-explore

**Launch parallel Explore agents** (using the Agent tool with `subagent_type: Explore`) for each changed project. Gather the same information as init:

- Basic info, structure, key files
- Dependencies and patterns
- External services
- Connections to other projects
- Environment variables

Compare findings against existing `services/[project].md` docs to identify what actually changed.

## Update Documentation

Use whatever format best communicates the architecture — Mermaid, ASCII, tables, prose. Optimize for clarity.

### CLAUDE.md

Update relevant sections:

- Projects table (add/remove/update)
- External Services table
- "How They Connect" diagram if relationships changed
- Key Locations for modified projects
- Patterns & Conventions if new patterns detected
- Keep it concise — link to detailed docs for depth

### OVERVIEW.md

If architectural changes detected:

- Update system diagram
- Update data flow descriptions
- Add new integration points

### services/[project].md

- Update docs for changed projects
- Create docs for new projects (use same template as init)
- Delete docs for removed projects

### services/external/[service].md

- Create docs for new external services
- Update if usage changed
- Remove if service no longer used

### tickets/

- Create `tickets/[new-project]/` for new projects
- Keep folders for removed projects (existing tickets may still be relevant)

## Flag Breaking Changes

If you detect potentially breaking changes, add a temporary section to CLAUDE.md:

```markdown
## Recent Changes (review needed)

- **[Project]**: [Change] — [Potential impact]
```

## Consistency Check

Before finalizing, verify:

- All expected files exist
- All service docs have consistent sections
- File paths point to real locations
- Project names match across documents
- CLAUDE.md is concise (no redundant info, links to detailed docs)

Fix any issues found.

## Summary

Report what was updated:

- Projects scanned
- Files modified
- Significant changes detected

---

Now check for changes and update the architecture documentation.

# Lore Update

Update architecture documentation after code changes.

## Goal

Efficiently detect what changed across projects, re-explore only the affected parts, and update the documentation to reflect current state.

## Detect Changes

Identify what needs updating:

- **New projects** — Folders with project markers not in current docs
- **Removed projects** — Documented projects whose folders no longer exist
- **Modified projects** — Projects with code changes (check git status where available, or compare against existing docs)
- **New external services** — New dependencies or environment variables
- **Changed relationships** — New API calls, imports, or integrations between projects

## Re-explore

**Explore changed projects in parallel.** Gather the same information as init:

- Basic info, structure, key files
- Dependencies and patterns
- External services
- Connections to other projects

Compare findings against existing `services/[project].md` docs to identify what actually changed.

## Formatting Rules

Follow the formatting rules from lore-init: box-drawing characters (`┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼`) for diagrams, tables for structured data, backticks for paths, short scannable paragraphs.

## Update Documentation

### CLAUDE.md

Update relevant sections:
- Projects table (add/remove/update)
- External Services table
- "How They Connect" diagram if relationships changed
- Key Locations for modified projects
- Patterns & Conventions if new patterns detected

### OVERVIEW.md

If architectural changes detected:
- Update system diagram
- Update data flow descriptions
- Add new integration points

### services/[project].md

- Update docs for changed projects
- Create docs for new projects
- Delete docs for removed projects

### services/external/[service].md

- Create docs for new external services
- Update if usage changed (new projects using them)
- Remove if service no longer used

### tickets/

- Create `tickets/[new-project]/` for new projects
- Keep folders for removed projects (existing tickets may still be relevant)

## Flag Breaking Changes

If you detect potentially breaking changes, add a temporary section to CLAUDE.md:

```markdown
## Recent Changes (review needed)

- **[Project]**: [Change] - [Potential impact]
```

## Consistency Check

Before finalizing, verify the updated documentation:

- **Files generated:** Confirm all expected files exist (CLAUDE.md, OVERVIEW.md, `services/*.md`)
- **Section consistency:** All service docs have the same sections in the same order
- **Valid references:** File paths in documentation point to real locations
- **Diagram alignment:** ASCII diagrams use box-drawing characters and are properly aligned
- **Naming consistency:** Project names match across all documents

Fix any issues found during this check.

## Summary

Report what was updated:
- Projects scanned
- Files modified
- Significant changes detected

---

Now check for changes and update the architecture documentation.

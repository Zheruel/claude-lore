# Lore Init

Generate architecture documentation for a multi-project codebase.

## Goal

Scan all sibling projects in the parent directory, understand their structure, relationships, and external dependencies, then generate comprehensive documentation that enables effective feature planning.

## Discovery

Find projects in `../` by looking for these markers:

| Marker | Tech Stack |
|--------|------------|
| `package.json` | Node.js / JavaScript / TypeScript |
| `*.csproj` or `*.sln` | .NET / C# |
| `pyproject.toml` or `requirements.txt` | Python |
| `pom.xml` | Java / Maven |
| `build.gradle` or `build.gradle.kts` | Java / Kotlin / Gradle |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `Gemfile` | Ruby |
| `composer.json` | PHP |

**Skip:** `node_modules`, `.git`, `bin`, `obj`, `dist`, `build`, `target`, `.venv`, `venv`, `__pycache__`, and this `architecture` folder.

## Exploration

**Explore all discovered projects in parallel.** For each project, gather:

- Basic info (name, tech stack, purpose)
- Directory structure and key files
- Entry points and configuration
- Major dependencies
- Architecture patterns
- External services (databases, APIs, cloud services)
- Development commands

Also detect relationships between projects: API calls, shared types, database connections, message queues.

Check for `external-services.yaml` in any project or the architecture folder for manually defined services.

## Formatting Rules

**ASCII Diagrams:**
- Use box-drawing characters: `┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼`
- Consistent spacing and alignment
- Label all connections with arrows and short descriptions
- Keep diagrams under 80 characters wide

**Document Structure:**
- Tables for structured data (projects, endpoints, services)
- Short paragraphs (3-4 lines max) for scannability
- Consistent heading hierarchy (h2 for sections, h3 for subsections)
- File paths always in backticks: `src/index.ts`
- Code blocks with language hints: ```typescript

**Dual Readability (AI + Human):**
- Explicit section headers (AI can locate info quickly)
- No abbreviations without first defining them
- Consistent naming across all documents
- Cross-references use exact file paths

## Output

Generate these files:

### CLAUDE.md

The main reference file. Structure:

```markdown
# [Platform Name]

## System Overview
[2-3 sentence description]

## Projects

| Project | Path | Tech | Purpose |
|---------|------|------|---------|
| ... | `../[folder]/` | ... | ... |

## External Services

| Service | Purpose | Used By |
|---------|---------|---------|
| ... | ... | ... |

## How They Connect

[ASCII diagram showing project relationships]

## Key Locations

**[Project] (`../[folder]/`):**
- [Category]: `path/`
...

## Patterns & Conventions

- [Pattern observed across projects]
...

## Building New Features

**[Feature type]:**
1. [Step with file path]
...

## Architecture Docs
- Full overview: `OVERVIEW.md`
- Per-project details: `services/[project].md`
- External services: `services/external/`

---

## Creating Tickets

Ask me to create a ticket for any feature or task. Before writing, I'll:
1. Read the architecture docs here (`services/*.md`, `OVERVIEW.md`) for context
2. Explore actual code in the project repos to understand current implementation
3. Identify the right files to modify and potential impacts

Tickets are saved to:
- `tickets/[project]/` - Single project changes
- `tickets/cross-project/` - Multi-project features

Tickets include implementation steps with specific file paths and are formatted for GitHub Issues.
```

### OVERVIEW.md

Detailed architecture document with:
- System architecture diagram (ASCII or mermaid)
- Data flow explanations
- Authentication/authorization flow
- Deployment architecture
- Database schema overview

### services/[project].md

Per-project documentation:

```markdown
# [Project Name]

## Overview
[Role in the system]

## Tech Stack
- **Runtime:** ...
- **Framework:** ...
- **Database:** ...
- **Key Libraries:** ...

## Directory Structure
[Tree with annotations]

## Key Files
- `[file]` - [purpose]

## API Endpoints (if applicable)
| Method | Path | Purpose |
|--------|------|---------|
| ... | ... | ... |

## Configuration
- `[config file]` - [what it configures]

## Development
- **Run:** `[command]`
- **Test:** `[command]`
- **Build:** `[command]`

## Connections
- **Calls:** [other services]
- **Called by:** [other services]
- **Database:** [database]
```

### services/external/[service].md

For each external service:

```markdown
# [Service Name]

## Purpose
[What it provides]

## Used By
- [Project] - [how it's used]

## Configuration
- Environment variables: `[VAR]`
- Config file: `[path]`

## Documentation
- [Official docs link]

## Local Development
[Setup instructions]
```

### tickets/

Create folder structure:
```
tickets/
├── [project-name]/
├── [project-name]/
└── cross-project/
```

Add `.gitkeep` files to each folder.

## Consistency Check

Before finalizing, verify the generated documentation:

- **Files generated:** Confirm CLAUDE.md, OVERVIEW.md, and `services/*.md` exist for each project
- **Section consistency:** All service docs have the same sections in the same order
- **Valid references:** File paths in documentation point to real locations
- **Diagram alignment:** ASCII diagrams use box-drawing characters and are properly aligned
- **Naming consistency:** Project names match across all documents

Fix any issues found during this check.

## Summary

After generating documentation, report:
- Projects discovered
- Technologies detected
- External services found
- Key relationships identified

---

Now scan the parent directory and generate the architecture documentation.

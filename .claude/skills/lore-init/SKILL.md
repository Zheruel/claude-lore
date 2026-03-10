---
name: lore-init
description: Scan all sibling projects and generate comprehensive architecture documentation for multi-project codebases
disable-model-invocation: true
---

# Lore Init

Generate architecture documentation for a multi-project codebase.

Ultrathink before beginning your analysis. You are mapping an entire system — take the time to deeply understand how everything connects before writing anything.

## Goal

Scan all sibling projects in the parent directory, understand their structure, relationships, and external dependencies, then generate comprehensive documentation that enables effective cross-service feature planning.

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
| `Dockerfile` (standalone) | Containerized service |

Also detect monorepo patterns: Nx (`nx.json`), Turborepo (`turbo.json`), Lerna (`lerna.json`), pnpm workspaces (`pnpm-workspace.yaml`). If a monorepo is found, document it as one project but catalog its packages/apps as sub-projects.

**Skip directories:** `node_modules`, `.git`, `bin`, `obj`, `dist`, `build`, `target`, `.venv`, `venv`, `__pycache__`, and the architecture folder itself.

## Exploration

**Launch parallel Explore agents** (using the Agent tool with `subagent_type: Explore`) for each discovered project. Each agent should gather:

- Basic info (name, tech stack, purpose)
- Directory structure and key files
- Entry points and configuration
- Major dependencies
- Architecture patterns (MVC, CQRS, microservices, etc.)
- External services used (databases, APIs, cloud services, message queues)
- Development commands (run, test, build, lint)
- Environment variables and their purposes

After all agents return, analyze the combined results to detect relationships between projects:
- API calls between services (look for HTTP clients, gRPC definitions, OpenAPI specs)
- Shared types, models, or contracts
- Database connections (shared databases, read replicas)
- Message queues and event-driven patterns
- Authentication flows that span services
- Shared environment variables pointing to the same resources

Check for `external-services.yaml` in any project or the architecture folder for manually defined services.

## Formatting

Use whatever format best communicates the architecture — Mermaid diagrams, ASCII art, tables, prose, or any combination. Optimize for clarity, not for any specific format. The documentation should be easy for both humans and AI to parse.

General guidelines:
- Tables for structured data (projects, endpoints, services)
- Short paragraphs (3-4 lines max) for scannability
- Consistent heading hierarchy
- File paths always in backticks: `src/index.ts`
- No abbreviations without first defining them
- Consistent naming across all documents
- Cross-references use exact file paths

## Output

Generate these files:

### CLAUDE.md

The main reference file that Claude loads every session. Keep it concise — only include what's needed for high-level orientation. Link to `OVERVIEW.md` and `services/*.md` for depth.

Structure:

```markdown
# [Platform Name]

## System Overview
[2-3 sentence description of the overall system]

## Projects

| Project | Path | Tech | Purpose |
|---------|------|------|---------|
| ... | `../[folder]/` | ... | ... |

## External Services

| Service | Purpose | Used By |
|---------|---------|---------|
| ... | ... | ... |

## How They Connect

[Diagram showing project relationships — use whatever format communicates it best]

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

Use `/lore-ticket [description]` to create implementation tickets.

### Ticket Guidelines
- Tickets are designed as input for Claude Code **plan mode**
- Never include code snippets — explain **what** to do and **why**
- Focus on architectural decisions and their rationale
- Reference specific file paths that need modification
- For frontend work, the ticket should note to use the `/frontend-design` skill during implementation
- Include edge cases, integration points, and testing strategy
- Keep it clear and concise — a good ticket is a good plan

### Ticket Locations
- `tickets/[project]/` — Single project changes
- `tickets/cross-project/` — Multi-project features
```

### OVERVIEW.md

Detailed architecture document with:
- System architecture diagram
- Data flow between services
- Authentication/authorization flow
- Deployment architecture (if detectable)
- Database schema overview
- Key integration patterns

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

## Data Models
[Key models/entities and their relationships]

## Configuration
- `[config file]` - [what it configures]

## Environment Variables
| Variable | Purpose |
|----------|---------|
| ... | ... |

## Development
- **Run:** `[command]`
- **Test:** `[command]`
- **Build:** `[command]`

## Connections
- **Calls:** [other services]
- **Called by:** [other services]
- **Database:** [database]
- **Events published:** [if applicable]
- **Events consumed:** [if applicable]
```

### services/external/[service].md

For each external service:

```markdown
# [Service Name]

## Purpose
[What it provides to the system]

## Used By
- [Project] - [how it's used]

## Configuration
- Environment variables: `[VAR]`
- Config file: `[path]`

## Local Development
[Setup instructions, mock options, sandbox accounts]
```

### tickets/

Create folder structure with `.gitkeep` files:
```
tickets/
├── [project-name]/
├── [project-name]/
└── cross-project/
```

## Consistency Check

Before finalizing, verify:

- All expected files exist (CLAUDE.md, OVERVIEW.md, `services/*.md`)
- All service docs have the same sections in the same order
- File paths in documentation point to real locations
- Project names match across all documents
- CLAUDE.md is concise (no redundant information, links to detailed docs for depth)

Fix any issues found.

## Summary

After generating, report:
- Projects discovered and their tech stacks
- External services found
- Key relationships identified
- Any architectural concerns or observations

---

Now scan the parent directory and generate the architecture documentation.

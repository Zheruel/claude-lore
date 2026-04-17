---
name: lore-init
description: Scan all sibling projects and generate a lean CLAUDE.md architecture index
disable-model-invocation: true
---

# Lore Init

Scan a multi-project codebase and produce a lean `CLAUDE.md` index for Claude to load each session. The index is a map for writing cross-service tickets — depth comes from live re-exploration in each affected repo, not from this file.

Ultrathink before beginning. You are mapping an entire system — understand how everything connects before writing anything.

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

Launch parallel Explore agents (Agent tool with `subagent_type: Explore`) for each discovered project. Each agent gathers:

- Name, tech stack, one-line purpose
- Directory structure and key entry points
- Major dependencies and architecture patterns
- External services used (databases, APIs, queues, cloud)
- API endpoints (if applicable)
- Environment variables
- Dev commands (run, test, build)

After agents return, analyze the combined results to detect cross-project relationships:

- API or RPC calls between services
- Shared types, models, or contracts
- Shared databases or read replicas
- Message queues and event patterns
- Authentication flows that span services
- Shared environment variables pointing to the same resources

Check for an `external-services.yaml` in any project or in the architecture folder for manually-declared services.

## Output — `CLAUDE.md` (lean index for Claude)

Write `CLAUDE.md` at the architecture folder root. Keep it tight: this file gets loaded into every Claude session, so every line should earn its place.

Required structure:

````markdown
# [Platform Name]

[One paragraph: what this system does, who it's for, the headline architecture pattern. 2-3 sentences max.]

## Projects

| Project | Path | Tech | Purpose |
|---------|------|------|---------|
| ... | `../[folder]/` | ... | ... |

## External Services

| Service | Purpose | Used By |
|---------|---------|---------|
| ... | ... | ... |

## Cross-Project Edges

```mermaid
graph LR
  [small diagram showing API calls, shared DBs, event flows between projects]
```

## Key Locations

_Rough starting points for live exploration, not a canonical catalog — always verify against current code before acting on them._

**[Project] (`../[folder]/`):**
- [Category]: `path/`
- [Category]: `path/`

[Repeat per project. Only the directories a plan-mode session would want to start from. No file-level catalog — that's what live exploration is for.]

## Patterns & Conventions

- [Pattern observed across projects]

## Creating Tickets

Use `/lore-ticket [description]` to create a cross-project architectural ticket.

- Tickets are architectural plans, not code. They explain *what* each affected service needs to do and *why*, never *how* at the code level.
- Tickets live flat at `tickets/[feature-name].md` (kebab-case).
- Tickets point to directories and key modules, not specific files or line numbers — plan mode picks the exact spot with full local context.
- The intended workflow is: paste the entire ticket into Claude Code plan mode inside each affected service repo. Each repo's plan mode produces the per-service implementation plan with full local context.
````

Hard constraints:

- No duplicated tech-stack prose. The projects table is the source of truth.
- No per-service deep sections. That's what live re-exploration in each repo is for.
- The Mermaid diagram should be small and focused on cross-project edges, not internal architecture.

## `tickets/` folder

Create the `tickets/` folder at the architecture root with a single `.gitkeep` inside. Flat. Every ticket from `/lore-ticket` will live as `tickets/[feature-name].md`.

## Consistency check

Before finishing, verify:

- `CLAUDE.md` exists, has the projects table, the cross-project Mermaid diagram, and the key locations section
- Every project's path actually points to a real folder

If any of these fail, fix them.

## Summary

Report to the user:

- Projects discovered (count + names)
- External services found
- Key cross-project relationships
- Where the index lives: `CLAUDE.md`
- Anything architecturally noteworthy or surprising you saw while exploring

---

Now scan the parent directory and generate the architecture index.

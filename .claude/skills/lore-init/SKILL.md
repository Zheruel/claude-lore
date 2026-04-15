---
name: lore-init
description: Scan all sibling projects and generate a lean CLAUDE.md index plus a self-contained architecture.html report
disable-model-invocation: true
---

# Lore Init

Scan a multi-project codebase and produce two artifacts: a lean `CLAUDE.md` for Claude to load each session, and a self-contained `architecture.html` for humans to read in a browser.

Ultrathink before beginning. You are mapping an entire system — understand how everything connects before writing anything.

## Two outputs, two audiences

- **`CLAUDE.md`** is for Claude. Lean, fast to load, no prose padding. Just the facts a plan-mode session needs to orient itself.
- **`architecture.html`** is for humans. Rich, navigable, browser-rendered. The full architecture documentation lives here.

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

## Output 1 — `CLAUDE.md` (lean index for Claude)

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

## Human Documentation

For the rich, navigable architecture overview, open `architecture.html` in a browser.

## Creating Tickets

Use `/lore-ticket [description]` to create a cross-project architectural ticket.

- Tickets are architectural plans, not code. They explain *what* each affected service needs to do and *why*, never *how* at the code level.
- Tickets live flat at `tickets/[feature-name].md` (kebab-case).
- Tickets point to directories and key modules, not specific files or line numbers — plan mode picks the exact spot with full local context.
- The intended workflow is: paste the entire ticket into Claude Code plan mode inside each affected service repo. Each repo's plan mode produces the per-service implementation plan with full local context.
````

Hard constraints:

- No duplicated tech-stack prose. The projects table is the source of truth.
- No per-service deep sections. That's what `architecture.html` and live re-exploration are for.
- The Mermaid diagram should be small and focused on cross-project edges, not internal architecture.

## Output 2 — `architecture.html` (rich human-facing report)

Write `architecture.html` at the architecture folder root. Single self-contained HTML file. No build step, no toolchain, no static-site generator. Open it with `open architecture.html` and you get everything.

### Required structure

A single HTML document with:

- `<!doctype html>`, `<head>` with title, charset, viewport, and a small inline `<style>` block
- One `<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>` tag (pinned to a major version so old generated reports keep rendering)
- One inline `<script>mermaid.initialize({startOnLoad: true});</script>` tag
- A `<body>` containing the sections below

### Required sections (in this order, each with an `id` for anchor navigation)

1. **Overview** — system description, headline architecture pattern, what makes this codebase different
2. **Projects** — table of all projects with name, path, tech stack, purpose, dev commands
3. **Architecture diagram** — one or more Mermaid diagrams (`<div class="mermaid">…</div>`) showing how the projects connect — API calls, shared databases, event flows. This is the centerpiece of the report.
4. **External services** — table or list of every external service (databases, queues, third-party APIs, cloud services) with purpose, used-by, configuration notes
5. **Data flows** — for each major flow in the system (e.g., a user request, an event, a background job), trace the path through the projects. Mermaid sequence diagrams work well here.
6. **Per-project deep dives** — one section per project with:
   - Tech stack details
   - Key files and entry points
   - API endpoints (if applicable)
   - Data models / key entities
   - Environment variables
   - Dev commands (run, test, build)
   - Connections (calls, called by, databases, events published, events consumed)
7. **Patterns & conventions** — patterns observed across projects (auth, error handling, logging, naming, deployment)
8. **Building new features** — short guides for the most common feature types in this codebase, with file-path anchors

### Style and rendering

- Plain semantic HTML: `<h1>`, `<h2>`, `<section>`, `<table>`, `<nav>`, `<code>`, `<pre>`
- Small inline `<style>` block. Aim for: max-width container, readable line length, monospace for code/paths, sticky in-page nav if practical
- Optimized for "open it and skim", not for design polish. No SPA, no JS framework, no fancy interactivity
- Mermaid blocks render client-side via the CDN script. The file degrades gracefully to plain text if offline (Mermaid blocks just stay as text)
- A small `<nav>` near the top with anchor links to each section so readers can jump around

### What goes in

- Everything a new engineer would want to read on day one to understand the system
- All per-project detail (tech stack, key files, endpoints, env vars, dev commands, connections)
- All diagrams, data flows, and architecture-level explanation

Reference file paths, don't paste source — the HTML report is *about* the codebase, not a copy of it.

## Output 3 — `tickets/` folder

Create the `tickets/` folder at the architecture root with a single `.gitkeep` inside. Flat. Every ticket from `/lore-ticket` will live as `tickets/[feature-name].md`.

## Consistency check

Before finishing, verify:

- `CLAUDE.md` exists, has the projects table, the cross-project Mermaid diagram, and the key locations section
- `architecture.html` exists, is a single self-contained file, includes the Mermaid CDN script tag, and contains all eight required sections
- Project names match between `CLAUDE.md` and `architecture.html`
- Every project's path in both files actually points to a real folder

If any of these fail, fix them.

## Summary

Report to the user:

- Projects discovered (count + names)
- External services found
- Key cross-project relationships
- Where the artifacts live: `CLAUDE.md` and `architecture.html`
- Anything architecturally noteworthy or surprising you saw while exploring

---

Now scan the parent directory and generate the two artifacts.

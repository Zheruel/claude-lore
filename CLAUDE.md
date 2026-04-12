# Architecture

Run `/lore-init` to scan your projects and generate the architecture artifacts.

## Skills

- `/lore-init` — Scan all projects and generate the lean `CLAUDE.md` index plus the human-facing `architecture.html` report
- `/lore-update` — Re-scan and regenerate both artifacts after code changes
- `/lore-ticket [description]` — Create an architectural implementation ticket for a feature or task

## What you get after init

Two artifacts, two audiences:

- **`CLAUDE.md`** — a lean index that Claude loads each session. Projects table, external services, a small Mermaid diagram of cross-project edges, key locations per project, patterns, and a pointer to the HTML report. Optimized for fast loading, not for human reading.
- **`architecture.html`** — a single self-contained HTML file with the rich, navigable architecture documentation. System overview, projects, architecture diagrams, external services, data flows, per-project deep dives, patterns. Open it in a browser. This is what humans read.

The `tickets/` folder is flat — every ticket lives at `tickets/[feature-name].md`.

## Ticket guidelines

Tickets are architectural plans, not code. They explain *what* each affected service needs to do and *why*, never *how* at the code level. The intended workflow is to paste the entire ticket into Claude Code plan mode inside each affected service repo — each repo's plan mode then produces the per-service implementation plan with full local context.

When creating tickets:

- Never include code snippets — explain what to do and why
- Focus on architectural decisions and their rationale
- Reference specific file paths that need modification
- For frontend work, note that the `/frontend-design` skill should be used during implementation
- Include edge cases, integration points, and testing strategy
- Keep it clear and concise

After writing a ticket, the `ticket-validator` agent runs as a senior-architect review: it re-explores the live code in each affected service to check the ticket against reality and flags weak architectural decisions.

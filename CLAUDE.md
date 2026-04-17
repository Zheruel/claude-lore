# Architecture

Run `/lore-init` to scan your projects and generate the architecture index.

## Skills

- `/lore-init` — Scan all projects and generate the lean `CLAUDE.md` architecture index
- `/lore-update` — Re-scan and regenerate the index after code changes
- `/lore-ticket [description]` — Create an architectural implementation ticket for a feature or task

## What you get after init

A lean `CLAUDE.md` that Claude loads each session: projects table, external services, a small Mermaid diagram of cross-project edges, key locations per project, and patterns. It's an index for writing cross-service tickets — depth comes from live re-exploration in each affected repo, not from this file.

The `tickets/` folder is flat — every ticket lives at `tickets/[feature-name].md`.

## Ticket guidelines

Tickets are architectural plans, not code. They explain *what* each affected service needs to do and *why*, never *how* at the code level. The intended workflow is to paste the entire ticket into Claude Code plan mode inside each affected service repo — each repo's plan mode then produces the per-service implementation plan with full local context.

When creating tickets:

- Never include code snippets — explain what to do and why
- Focus on architectural decisions and their rationale
- Point to directories and key modules, not specific files or line numbers — plan mode picks the exact spot with full local context
- Include edge cases, integration points, and testing strategy
- Keep it clear and concise

After writing a ticket, the `ticket-validator` agent runs as a senior-architect review: it re-explores the live code in each affected service to check the ticket against reality and flags weak architectural decisions.

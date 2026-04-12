# Claude Lore

Two artifacts that keep Claude Code grounded in your multi-project codebase: a lean index Claude loads each session, and a rich HTML report humans actually read.

## What it does

Claude Lore scans every project in your codebase, maps the relationships between them, and generates two things:

- **`CLAUDE.md`** — a lean index that Claude Code loads automatically. Projects table, external services, a small cross-project diagram, key locations. Optimized for fast loading, not human browsing.
- **`architecture.html`** — a single self-contained HTML file with the full architecture documentation: system overview, diagrams, data flows, per-project deep dives, external services, patterns. Open it in a browser. This is what humans read.

Tickets created by `/lore-ticket` re-explore the live code each time, so they're always grounded in current reality.

## Quick Start

```bash
git clone https://github.com/tinzeljar/claude-lore.git architecture
cd architecture && claude
/lore-init
```

## What you get

```
my-company/
├── architecture/
│   ├── CLAUDE.md          # Lean index, auto-loaded by Claude
│   ├── architecture.html  # Rich human-facing architecture report
│   └── tickets/           # Flat folder, one ticket per file
│       └── add-rate-limiting.md
├── api/
├── frontend/
└── ...
```

The HTML report holds the rich documentation; the lean `CLAUDE.md` is for Claude.

## What you can do after init

**`/lore-ticket rate limiting for the API`**
> Re-explores the live code across affected services and writes an architectural ticket optimized for plan mode. A senior-architect agent then reviews it against the live code.

**Open `architecture.html`**
> Browse the full architecture: diagrams, data flows, per-project deep dives, external services.

**"How does authentication work?"**
> Claude has the lean index and re-explores the actual code to answer.

**"Add user notifications to the platform"**
> Claude knows which projects to look at and traces the impact across them.

## The intended ticket workflow

1. Run `/lore-ticket "the feature description"` inside the architecture folder.
2. The skill re-explores the live code in every affected project and writes one shared architectural ticket at `tickets/[feature-name].md`. The ticket-validator agent reviews it.
3. Open Claude Code in plan mode inside each affected service repo and paste the *whole* ticket. Each repo's plan mode produces the per-service implementation plan with full cross-service context plus its own local context.

That's why tickets aren't split per service — every service benefits from seeing the whole shared brief.

## Skills

| Skill | Description |
|-------|-------------|
| `/lore-init` | Scan all projects, write the lean `CLAUDE.md` and the rich `architecture.html` |
| `/lore-update` | Re-scan and regenerate both artifacts |
| `/lore-ticket [description]` | Create an architectural implementation ticket |

## Supported tech stacks

| Marker | Stack |
|--------|-------|
| `package.json` | Node.js / TypeScript |
| `*.csproj` / `*.sln` | .NET / C# |
| `pyproject.toml` / `requirements.txt` | Python |
| `pom.xml` | Java / Maven |
| `build.gradle` | Java / Kotlin / Gradle |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `Dockerfile` | Containerized services |
| `nx.json` / `turbo.json` / `lerna.json` | Monorepos |

## License

MIT

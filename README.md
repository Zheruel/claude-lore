# Claude Lore

Turn CLAUDE.md into a living system brain that understands your entire multi-project codebase.

## What It Does

Claude Lore scans all projects in your codebase, maps their relationships, and generates comprehensive documentation that Claude Code loads automatically. Every future session starts with full context about your system architecture, tech stacks, and how everything connects.

## Quick Start

```bash
git clone https://github.com/tinzeljar/claude-lore.git architecture
cd architecture && claude
/lore-init
```

## What You Get

```
my-company/
├── architecture/
│   ├── CLAUDE.md         # System context (auto-loaded by Claude)
│   ├── OVERVIEW.md       # Architecture diagrams and data flows
│   ├── services/
│   │   ├── api.md        # Per-project documentation
│   │   ├── frontend.md
│   │   └── external/
│   │       └── stripe.md # External service docs
│   └── tickets/
│       ├── api/
│       ├── frontend/
│       └── cross-project/
├── api/
├── frontend/
└── ...
```

## What You Can Do After Init

**"Add user notifications to the platform"**
→ Claude knows which projects need changes, where the relevant code lives, and how they connect

**"Create a ticket for rate limiting"**
→ Claude reads the architecture docs, explores the actual code, then writes a detailed implementation plan with specific file paths

**"How does authentication work?"**
→ Claude explains the flow across all your services with file references

**"What would break if I change the user schema?"**
→ Claude traces the impact across projects

## Commands

| Command | Description |
|---------|-------------|
| `/lore-init` | Scan all projects, generate full documentation |
| `/lore-update` | Update docs after code changes |

## Cross-Project Tickets

When you ask for a feature that spans multiple services, Claude creates tickets in `tickets/cross-project/` with:
- Implementation steps for each affected project
- The order to make changes
- Integration points and potential issues
- Specific file paths to modify

## Supported Tech Stacks

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

## License

MIT

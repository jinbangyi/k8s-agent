# CLAUDE.md

## Project Overview

TODO: Add a brief project description here.

## Repository Structure

```
.
├── .ai/summaries/                     # AI-generated summaries (date-based: YY-MM-DD/)
│   └── 26-01-09/                      # summaries for Jan 9, 2026
├── .claude/                           # Claude Code configuration (agents, commands, skills)
│   ├── agents/                        # Claude agents definitions
│   │   └── update-readme.md           # Agent for create/updating README files for a directory
│   ├── commands/                      # Claude command definitions
│   │   ├── bug-review-and-fix.md      # Command for bug review and fix
│   │   ├── code-review.md             # Command for code review
│   │   ├── commit.md                  # Command for commit message generation
│   │   └── update-root-docs.md        # Command for updating root documentation files
│   ├── draft/                         # Drafting workflows for creating Claude Code agents/commands
│   ├── skills/                        # Claude skill definitions
│   │   └── planning-with-files.md     # Skill for planning taskss, ref: https://github.com/OthmanAdi/planning-with-files
│   ├── rules.md                       # Project rules and guidelines for AI agents
│   └── settings.json                  # Claude Code settings
├── .devcontainer/                     # Development container runtime configuration
│   ├── .env.example                   # Example environment variables file
│   └── docker-compose.yaml            # Docker Compose file for devcontainer
├── debug/                             # Temporary debugging files ONLY
├── docs/                              # Project documentation
│   ├── AI-external-context/           # External system context for AI agents
│   │   └── local.md                   # Local running environment info
│   ├── blogs/                         # Blog posts and articles (best practices, tutorials, solutions)
│   ├── development/                   # Date-based development plans (YY-MM-DD/)
│   │   └── 26-01-09/                  # development notes for Jan 9, 2026
│   ├── requirements/                  # Requirements documentation, specs, and user stories
│   │   └── feature-xx/                # Feature-specific requirements
│   ├── user-guide/                    # User guides and manuals
│   ├── rules.md                       # Repository rules and guidelines
│   └── TODO.md                        # Active TODO list (unfinished tasks only)
├── scripts/                           # Repository scripts (to be implemented)
├── src/                               # All source code (to be implemented)
├── .dockerignore                      # Docker ignore file
├── .gitignore                         # Git ignore file
├── CLAUDE.md                          # Project overview and guidelines for AI agents
├── main.py                            # Main application entry point (to be implemented)
├── pyproject.toml                     # Python project configuration (to be implemented)
├── README.md                          # Project README file (to be implemented)
└── uv.lock                            # Python dependency lock file (to be implemented)
```

## Development Workflow

### Date-Based Organization

- Development notes: `docs/development/YY-MM-DD/`
- AI summaries: `.ai/summaries/YY-MM-DD/`
- Use this format for all new development work

### Context Sources (in priority order)

1. `docs/development/` - Current plans and architecture
2. `docs/TODO.md` - Pending work
3. `.ai/summaries/` - Past AI work and decisions
4. `docs/AI-external-context/` - External system context

### File Organization Rules

- All source code → `src/`
- All scripts → `scripts/`
- Temporary debugging → `debug/` (never commit this)
- Documentation → `docs/development/YY-MM-DD/`

## Important Notes

2. **Always check `docs/development/`** for current plans before implementing
3. **Date-based file organization** for all new documentation
4. **TODO.md is for unfinished tasks only** - remove completed items

## Rules

### 📌 Mermaid Diagram Rules

**1. Syntax Case Sensitivity**
- All Mermaid keywords are case-sensitive
- Always use lowercase keywords (e.g. `graph`, `subgraph`, `classDef`)
- Incorrect casing (e.g. `Graph` or `ClassDef`) causes parsing errors

**2. Valid Node Labels**
- Do NOT use HTML tags in node labels (e.g. `<br/>`, `<b>`, `<i>`)
- Keep labels simple and descriptive
- Use parentheses or separate nodes for additional information

**3. Diagram Structure**
- For complex architectures with nested subgraphs, use `graph TD` (top-down) layout for readability
- Use clear, consistent node naming with hyphen separators (e.g. `dmz-subnet` instead of `dmzSubnet`)
- Group related nodes within subgraphs for logical organization

**4. Styling Guidelines**
- Use `classDef` to define reusable styles
- Keep class names simple and descriptive
- Use consistent color schemes for similar resource types

**5. Validation**
- Always validate diagrams using `mmdc` (Mermaid CLI)
- Example command: `mmdc -t neutral -i diagram.mmd -o diagram.svg`
- Fix any parsing errors before committing

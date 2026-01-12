# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**k8s-agent** is a full company resource management gitops based repo.

## Repository Structure

```
.
├── .ai/summaries/              # AI-generated summaries (date-based: YY-MM-DD/)
├── .claude/                    # Claude Code configuration (agents, commands, skills)
├── debug/                      # Temporary debugging files ONLY
├── docs/
│   ├── development/            # Date-based development plans (YY-MM-DD/)
│   │   ├── 26-01-08/          # Initial planning
│   │   └── 26-01-09/          # Architecture + phase plans
│   ├── requirements/           # Requirements documentation
│   └── TODO.md                # Active TODO list (unfinished tasks only)
├── src/                       # All source code (to be implemented)
└── scripts/                   # Repository scripts (to be implemented)
```

## Development Workflow

### Date-Based Organization
- Development notes: `docs/development/YY-MM-DD/`
- AI summaries: `.ai/summaries/YY-MM-DD/`
- Use this format for all new development work

### TODO Management
- `docs/TODO.md` contains **ONLY unfinished tasks**
- Remove completed items immediately
- Check this file before starting new work

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

## Key Architecture Decisions

### GitOps Philosophy
- All infrastructure changes tracked in git
- ArgoCD auto-syncs manifests to cluster
- Declarative configuration (Kubernetes manifests)
- Rollback via git revert

## Important Notes

2. **Always check `docs/development/`** for current plans before implementing
6. **Date-based file organization** for all new documentation
7. **TODO.md is for unfinished tasks only** - remove completed items

### 📌 Mermaid Syntax Rule

**Mermaid keywords are case-sensitive.**
Always use lowercase keywords (e.g. `graph`, `subgraph`, `style`).
Using incorrect casing (e.g. `Style` instead of `style`) will cause parsing errors.

# k8s-agent Project Context

## Repository Purpose

This repository (k8s-agent) is a comprehensive Kubernetes lifecycle management system that includes:
- Kubernetes cluster creation, management, and monitoring
- GitOps-based management of Kubernetes manifests
- Complete infrastructure-as-code for K8s operations

## Repository Structure

```
.
├── .ai/
│   └── summaries/          # AI-generated summaries (date-based folders: 26-01-08/)
├── .devcontainer/          # Docker Compose configs for development environment
├── .claude/                # Claude Code configuration
├── debug/                  # Temporary debugging files
├── docs/
│   ├── AI-external-context/ # External context docs for AI understanding
│   ├── biz/                # Business logic documentation
│   ├── development/        # Development plans, notes, and logs
│   │   ├── 26-01-08/       # Date-based dev notes
│   │   └── 26-01-09/
│   ├── requirements/       # All requirements documentation
│   └── TODO.md            # Active TODO list (unfinished tasks only)
├── src/                    # All source code and K8s manifests
└── scripts/                # Repository scripts
```

## Working Conventions

### Architecture Rules
- API layer and Telegram bot layer MUST share the same business logic code
- Separate API layer and TG bot layer from business logic layer
- Use adapters pattern for external integrations

### Development Workflow
- Date-based organization for development docs and AI summaries (format: YY-MM-DD)
- TODO.md contains ONLY unfinished tasks
- All temporary debugging files go in `debug/` directory
- Use Docker Compose for local development environment

### File Organization
- Source code lives in `src/`
- Scripts go in `scripts/`
- Documentation is date-organized under `docs/development/`
- AI outputs are date-organized under `.ai/summaries/`

## Key Context for Tasks

When working on this repository:
1. Always check `docs/development/` for current plans and notes
2. Check `docs/TODO.md` for pending work
3. Review existing AI summaries in `.ai/summaries/` for context
4. Follow the separation of concerns between API/TG bot and business logic
5. Place all temporary files in `debug/` directory
6. Document new development work in date-based folders

## GitOps & Kubernetes

This repository manages K8s manifests through GitOps principles:
- All infrastructure changes are tracked in git
- Manifests are stored in `src/` directory
- Use `.devcontainer/` configs for local environment setup

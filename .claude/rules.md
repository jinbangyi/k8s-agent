# k8s-agent Project Rules

## Architecture Principles
- API layer and Telegram bot layer MUST share the same business logic code
- Separate API layer and TG bot layer from business logic layer
- Follow the adapters pattern for external integrations

## File Organization Rules
- All source code goes in `src/`
- All scripts go in `scripts/`
- Documentation organized by date under `docs/development/YY-MM-DD/`
- AI summaries organized by date under `.ai/summaries/YY-MM-DD/`
- Temporary debugging files ONLY in `debug/` directory

## Documentation Rules
- TODO.md contains ONLY unfinished tasks (remove completed items)
- Development notes go in date-based folders
- Always check existing docs and summaries before starting new work

## GitOps & Manifest Rules
- All K8s manifests stored in `src/`
- All infrastructure changes tracked in git
- Use GitOps principles for cluster management

## Development Workflow
- Use `.devcontainer/` Docker Compose configs for local environment
- Reference `docs/AI-external-context/` for external system context
- Keep business logic shared between API and TG bot layers
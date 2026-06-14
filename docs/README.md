# Documentation

Project documentation for the AI Knowledge Workspace.

## Design System

**All frontend phases must follow the global UI/UX design system.**

See [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) for colors, typography, layout, animations, and component guidelines.

Implementation: `frontend/src/app/globals.css`, `frontend/src/lib/motion.ts`, `frontend/src/components/`

## Phase 01

Phase 01 establishes the monorepo foundation:

- Next.js frontend shell with design system
- FastAPI backend with health endpoint
- PostgreSQL with Alembic migrations
- Docker Compose development environment

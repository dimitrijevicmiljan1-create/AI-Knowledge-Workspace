# AI Knowledge Workspace

AI Knowledge Workspace is a SaaS application for organizing, searching, and querying knowledge with AI. This repository is a monorepo containing the frontend, backend, infrastructure, and documentation.

Phase 01 establishes the project foundation — architecture and infrastructure only. Authentication, AI features, chat, knowledge sources, and integrations are intentionally out of scope for this phase.

## Project Overview

The application is structured as a monorepo:

```text
ai-knowledge-workspace/
├── frontend/          # Next.js 15 web application
├── backend/           # FastAPI API server
├── docs/              # Project documentation
├── docker/            # Docker-related notes
├── docker-compose.yml # Local development stack
├── .env.example       # Environment variable template
└── README.md
```

## Tech Stack

### Frontend

- Next.js 15
- TypeScript
- Tailwind CSS
- shadcn/ui

### Backend

- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic
- PostgreSQL

### Infrastructure

- Docker
- Docker Compose

## Local Setup

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (optional, for local frontend development)
- Python 3.12+ (optional, for local backend development)

### Quick Start

1. Clone the repository:

```bash
git clone https://github.com/dimitrijevicmiljan1-create/ai-knowledge-workspace.git
cd ai-knowledge-workspace
```

2. Create your environment file:

```bash
cp .env.example .env
```

3. Start the full stack:

```bash
docker compose up
```

4. Verify the services:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

Expected health response:

```json
{
  "status": "ok"
}
```

## Development Commands

### Docker

```bash
# Start all services
docker compose up

# Start in detached mode
docker compose up -d

# Rebuild containers
docker compose up --build

# Stop services
docker compose down
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Database Migrations

```bash
cd backend
alembic revision -m "describe change"
alembic upgrade head
alembic downgrade -1
```

## Phase 01 Scope

Included:

- Monorepo structure
- Frontend layout with placeholder pages
- FastAPI application with `/health`
- PostgreSQL connection and Alembic setup
- Docker Compose development environment

Not included:

- Authentication
- AI features
- Chat
- Knowledge sources
- Integrations
- Business logic
//////

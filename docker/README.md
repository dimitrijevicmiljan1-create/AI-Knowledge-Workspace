# Docker

Docker configuration lives at the repository root in `docker-compose.yml`.

Services:

- `frontend` — Next.js application (port 3000)
- `backend` — FastAPI application (port 8000)
- `postgres` — PostgreSQL database (port 5432)

Start the stack from the project root:

```bash
docker compose up
```

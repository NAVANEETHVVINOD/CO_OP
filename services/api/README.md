# Co-Op Backend — FastAPI Control Plane

The central API for Co-Op Autonomous Company OS.
Handles authentication, document management, RAG search, chat streaming, agent orchestration, and human‑in‑the‑loop approvals.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview
This is the backend service for Co-Op. It is a FastAPI application that provides:

- REST API for frontend and CLI
- Server‑Sent Events (SSE) for streaming chat
- Background task queue via ARQ (async Redis queue)
- LangGraph agents (Lead Scout, Proposal Writer, etc.)
- Database models with PostgreSQL and Alembic migrations
- Vector search via Qdrant (or pgvector)
- File storage via MinIO
- LLM integration via LiteLLM (local Ollama or external APIs)

The service runs inside a Docker container but can also be run locally for development.

## Technology Stack

| Category | Tools |
|----------|-------|
| Web Framework | FastAPI |
| Async Database | SQLAlchemy 2.0 + asyncpg |
| Migrations | Alembic |
| Background Tasks | ARQ (async Redis queue) |
| Agents | LangGraph |
| LLM Gateway | LiteLLM |
| Vector Search | Qdrant (or pgvector) |
| Object Storage | MinIO (S3‑compatible) |
| Caching / Queue | Redis |
| Authentication | JWT (python‑jose) |
| Observability | OpenTelemetry, Prometheus, structlog |

## Project Structure

```text
services/api/
├── app/
│   ├── agent/                 # LangGraph agents and nodes
│   │   ├── graph.py           # Agent graph definition
│   │   ├── nodes.py           # Individual node logic
│   │   └── state.py           # Agent state (TypedDict)
│   ├── communication/         # Telegram bot (in‑process, Stage 2+)
│   ├── core/                  # Shared utilities (security, Redis, MinIO, etc.)
│   ├── crons/                 # Scheduled tasks (system monitor, morning brief)
│   ├── db/                    # Database models, sessions, repositories
│   ├── events/                # Redis consumer for document ingestion
│   ├── routers/               # API route handlers
│   ├── services/              # Business logic (search, chunking, indexing)
│   └── main.py                # FastAPI application entry point
├── alembic/                   # Database migrations
├── tests/                     # Pytest test suite
├── uploads/                   # Temporary file storage (for local dev)
├── .env.example               # Example environment variables
├── Dockerfile                 # Multi‑stage build for production
├── pyproject.toml             # Project dependencies
├── pyrightconfig.json         # Type checker configuration
└── README.md                  # This file
```

## Running the Backend

### With Docker (recommended for production)
The backend is part of the full Docker Compose stack. From the repository root:

```bash
cd infrastructure/docker
docker compose up -d co-op-api
```

The service will be available at http://localhost:8000.

### Without Docker (for development)

#### Prerequisites
- Python 3.12+
- PostgreSQL 16 (running)
- Redis 7 (running)
- Qdrant (optional; can use pgvector)
- MinIO (optional)

#### Setup
```bash
cd services/api
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
```
Edit `.env` and set the correct database, Redis, etc. URLs.

#### Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Run background workers (ARQ)
In a separate terminal:
```bash
arq app.worker.WorkerSettings
```
The worker handles cron tasks (Lead Scout, system monitor, etc.) and can be run independently.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async connection | `postgresql+asyncpg://coop:pass@localhost:5432/coop` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` |
| `QDRANT_URL` | Qdrant HTTP endpoint | `http://localhost:6333` |
| `MINIO_URL` | MinIO endpoint (host:port) | `localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO access key | |
| `MINIO_SECRET_KEY` | MinIO secret key | |
| `SECRET_KEY` | JWT signing secret | `change‑me` |
| `DB_PASS` | Database password | |
| `ENVIRONMENT` | development / production | `development` |
| `LITELLM_URL` | LiteLLM gateway (Stage 2+) | `http://localhost:4000` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (Stage 2+) | `(optional)` |
| `GROQ_API_KEY` | Groq API key (Stage 2+) | `(optional)` |
| `GEMINI_API_KEY` | Gemini API key (Stage 2+) | `(optional)` |

## API Endpoints

| Prefix | Description |
|--------|-------------|
| `/v1/auth` | Login, token refresh |
| `/v1/health` | Health checks (database, Redis, etc.) |
| `/v1/documents` | Upload, list, delete documents |
| `/v1/search` | Semantic search over documents |
| `/v1/chat` | Chat with streaming (SSE) |
| `/v1/conversations` | Manage chat history |
| `/v1/approvals` | Human‑in‑the‑loop actions |
| `/v1/costs` | Token usage (Stage 2+) |
| `/v1/settings` | Hardware tier, configuration (Stage 2+) |

For detailed API documentation, visit http://localhost:8000/docs (Swagger UI) when the server is running.

## Database Migrations

Migrations are managed with Alembic.

Create a new migration:
```bash
cd services/api
alembic revision --autogenerate -m "description"
```

Apply all pending migrations:
```bash
alembic upgrade head
```
Migrations are stored in `alembic/versions/`. The initial schema includes `tenant_id` on all tables for multi‑tenancy.

## Testing

Run the test suite with:
```bash
cd services/api
pytest tests/ -v
```
The tests use a separate database (SQLite or a test PostgreSQL) and mock external services.

## Adding a New Agent
1. Define the agent state in `app/agent/state.py` (TypedDict).
2. Create nodes in `app/agent/nodes.py`.
3. Build the graph in `app/agent/graph.py`.
4. Add a cron task or a trigger in `app/worker.py` to start the agent.
5. Write tests in `tests/test_agent.py`.

## Observability
- Logging is configured with `structlog` and correlates request IDs.
- Prometheus metrics are exposed at `/metrics` (via `prometheus_fastapi_instrumentator`).
- OpenTelemetry traces are sent to the collector (when configured).

## Security
- JWT tokens with short expiry, stored in HTTP‑only cookies (or localStorage in frontend).
- Passwords hashed with bcrypt.
- Rate limiting via slowapi.
- Input validation with Pydantic models.
- (Stage 3) LLM Guard for prompt injection detection.

## License
Apache License 2.0 – See LICENSE in the repository root

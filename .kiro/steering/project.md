---
inclusion: auto
---

# Co-Op Project Identity

## What This Is

Co-Op is a self-hosted Enterprise AI Operating System (Apache 2.0 license) — comparable to Microsoft Copilot + Glean AI + Zapier, but 100% on-premises with no cloud vendor dependency.

**GitHub:** https://github.com/NAVANEETHVVINOD/CO_OP

## Current Phase Status

### Phase 0 — Near Complete
- Backend: Full RAG pipeline working (upload → parse → chunk → embed → Qdrant)
- Hybrid search: BM25 + dense vectors, RRF merge, cross-encoder rerank
- LangGraph research agent: retrieve → rerank → generate (stubbed LLM, no API key needed)
- SSE streaming chat with citation events
- JWT authentication with PostgreSQL, Redis, MinIO, Qdrant all running in Docker
- Frontend: Dark dashboard UI rebuilt with 10 pages (login, dashboard, chat, documents, search, agents, approvals, admin)

### What's Working (DO NOT CHANGE)
- Full RAG pipeline end-to-end
- Hybrid search with citations
- SSE streaming chat
- JWT auth with protected routes
- All Docker services healthy

### What Needs Fixing
1. `conversations.tenant_id` column missing → run `alembic upgrade head`
2. Docker `DB_PASS` env var verification in docker-compose
3. `python-multipart` dependency check in pyproject.toml

### Phase 1 — Not Started
Keycloak SSO, LLM Guard, Traefik, RAGFlow full parsing, Temporal workflows, Docker Swarm deployment

## Tech Stack

### Frontend
- Next.js 16 with App Router + React 19
- Tailwind CSS 4 + shadcn/ui components
- Zustand (global state) + TanStack Query v5 (server state)
- SSE for streaming responses

### Backend
- FastAPI 0.111+ with async/await
- SQLAlchemy 2.0 (async) + Alembic migrations
- LangGraph 0.2+ for agent orchestration
- Pydantic v2 for schemas

### AI/Knowledge
- Qdrant 1.12.4 vector database (HNSW index)
- sentence-transformers (all-MiniLM-L6-v2, 384-dim embeddings)
- LangGraph stateful agents
- LiteLLM gateway (stubbed, no LLM API key required)

### Infrastructure
- PostgreSQL 16 (users, documents, conversations, audit)
- Redis 7 (event streams, cache)
- MinIO (S3-compatible document storage)
- Docker Compose (Phase 0) → Swarm (Phase 1) → Kubernetes (Phase 2+)

### Build System
- Turborepo monorepo
- pnpm workspace (Node >=20.0.0)
- Python 3.12+

## Test Credentials

```
Admin user:   admin@co-op.local / testpass123
Default tenant: co-op (auto-created on startup)
```

## Environment Variables

### Required: `infrastructure/docker/.env`
```env
DB_PASS=cooppassword123
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
SECRET_KEY=super-secret-key-change-in-production-min-32-chars
```

### Required: `apps/web/.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Common Commands

### Start all services
```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

### Check service health
```bash
docker compose -f infrastructure/docker/docker-compose.yml ps
curl http://localhost:8000/health
```

### Run database migrations
```bash
cd services/api
alembic upgrade head
```

### Build frontend
```bash
cd apps/web
pnpm install
pnpm build
```

### Development
```bash
# Root (runs all workspaces)
pnpm dev

# Frontend only
cd apps/web && pnpm dev

# Backend (in Docker)
docker compose -f infrastructure/docker/docker-compose.yml logs co-op-api -f
```

### Rebuild API after Python changes
```bash
docker compose -f infrastructure/docker/docker-compose.yml build co-op-api
docker compose -f infrastructure/docker/docker-compose.yml up -d co-op-api
```

## Multi-Agent Vision (Phase 2+)

Co-Op will support 8 specialist agents working together:
1. Research Agent (Phase 0 — read-only, working now)
2. Support Agent (Phase 2)
3. Code Agent (Phase 2)
4. Analytics Agent (Phase 2)
5. Communication Agent (Phase 2)
6. HR Agent (Phase 2)
7. Orchestrator Agent (Phase 3)
8. Memory Agent (Phase 3, Graphiti)

All agents pause at LangGraph `interrupt()` checkpoints for Human-in-the-Loop (HITL) approval before executing any state-changing actions.

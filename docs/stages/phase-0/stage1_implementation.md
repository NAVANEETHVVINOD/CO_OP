# Stage 1 — The Foundation
## Implementation Guide

**What this stage delivers:** A working Company GPT chatbot with document upload, search, and chat. You can demo this to anyone. The full RAG pipeline is functional end-to-end.

**Services (6):** co-op-api, co-op-web, postgres, redis, qdrant, minio

**Timeline:** This week

---

## What You Get

- Upload a PDF → AI answers questions about it (from RAG chunks, no LLM key needed)
- Login, dashboard, search, and chat all work
- Dark themed dashboard with health indicators
- Complete CI-ready codebase on GitHub

## What You Do NOT Have Yet (And That's Fine)

- Real LLM responses (still stubbed — fixed in Stage 2)
- Telegram control
- Any real agents
- Any external API calls

---

## Key Architectural Decisions

### Why Stubbed Inference?
The chat endpoint assembles answers from RAG chunks without calling any LLM. This is intentional — it lets you verify the entire pipeline works before spending time on LLM setup. When you add Ollama in Stage 2, the change is one function in `nodes.py`.

### Why Qdrant (Not pgvector)?
Qdrant is already configured and working. You could replace it with pgvector to save ~500MB RAM, but only do that in Stage 2 if RAM is genuinely a problem. Don't fix what isn't broken.

### Why No Keycloak/SSO?
Simple JWT auth (username + password → token) is enough for a solo developer. Keycloak adds complexity you only need when you have multiple users or enterprise clients. That's Stage 4 territory.

---

## Implementation Steps

### 1. Fix the Three Bugs

```bash
# Bug 1: Add env vars to docker-compose.yml
# Open infrastructure/docker/docker-compose.yml
# Add to co-op-api service > environment:
#   DATABASE_URL, DB_PASS, REDIS_URL, QDRANT_URL,
#   MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY,
#   SECRET_KEY, ENVIRONMENT, PYTHONPATH

# Bug 2: Run migration
docker exec co-op-api alembic upgrade head

# Bug 3: Add python-multipart
# Edit services/api/pyproject.toml, add "python-multipart>=0.0.9"
docker compose build co-op-api && docker compose up -d co-op-api
```

### 2. Verify Everything

```bash
# All containers healthy
docker compose ps

# Backend health
curl http://localhost:8000/health

# Auth works
curl -X POST http://localhost:8000/v1/auth/token \
  -d "username=admin@co-op.local&password=testpass123"

# Frontend builds
cd apps/web && pnpm build
```

### 3. Test the User Flow

1. Open http://localhost:3000 → should redirect to /login
2. Login → should reach /dashboard
3. Dashboard → health dots should be green
4. /documents → upload a PDF → wait for READY
5. /search → query about the PDF → results appear
6. /chat → ask a question → streaming response + citations

### 4. Ship It

```bash
git add .
git commit -m "feat: Stage 1 complete — RAG pipeline + dark dashboard"
git push origin main
git tag v0.1.0 -m "Stage 1: Company GPT working end-to-end"
git push origin v0.1.0
```

---

## How to Verify Stage 1 Is Complete

| Check | Command / Action | Expected Result |
|-------|-----------------|-----------------|
| All containers up | `docker compose ps` | 6 rows, all "Up (healthy)" |
| Health endpoint | `curl localhost:8000/health` | All services "ok" |
| Auth works | `POST /v1/auth/token` | JWT token returned |
| Frontend builds | `pnpm build` | Exit code 0 |
| Upload works | Upload PDF on /documents | Status reaches READY |
| Search works | Query on /search | Results with scores |
| Chat works | Ask question on /chat | Streaming response |
| Console clean | DevTools Console | Zero red errors |
| GitHub tag | Check GitHub Tags | v0.1.0 visible |

---

## Common Pitfalls

1. **Using `localhost` inside Docker** — Use service names: `postgres`, `redis`, `qdrant`, `minio`
2. **Forgetting to rebuild** — After changing `pyproject.toml`, you must `docker compose build co-op-api`
3. **Committing .env** — Double-check `.gitignore` before pushing
4. **Skipping "Done when" checks** — Run the actual verification, don't just eyeball the code

# Co-Op — Project Reference (Solo Developer Edition)

> This file is the master reference for the Co-Op project.
> Read this before making any changes.
> **AI IDE: Scan and understand this file completely before writing any code.**

---

## Documents to Scan First

Before starting ANY work, scan these files:

1. **This file** (`docs/stages/phase-0/PROJECT.md`) — Project identity, current state
2. **`docs/rules/co-op-solo-guidelines.mdc`** — Stage constraints, technology matrix
3. **`docs/rules/co-op-critical-constraints.mdc`** — Hard rules
4. **`docs/stages/phase-0/TASKS.md`** — Current phase task list
5. **`docs/stages/phase-0/stage1_implementation.md`** — Current stage guide
6. **`docs/rules/co-op-api-contracts.mdc`** — API endpoints + schema
7. **`services/api/app/config.py`** — Backend configuration
8. **`infrastructure/docker/docker-compose.yml`** — Service configuration

---

## What This Project Is

**Co-Op** = Self-hosted Autonomous Company Operating System (Apache 2.0)

An AI platform where agents find freelance clients, write proposals,
communicate professionally, track projects, and create invoices.
Every important action requires human approval via Telegram or dashboard.

**For:** Solo developers who want to automate their freelance business.
**Comparable to:** Microsoft Copilot + Glean AI + Zapier (but self-hosted, open source)

**GitHub:** https://github.com/NAVANEETHVVINOD/CO_OP

---

## Current State (Stage 1 — Near Complete)

### ✅ Working (DO NOT CHANGE)
- Full RAG pipeline: upload → parse → chunk → embed → Qdrant index
- Hybrid search: BM25 + dense vectors, RRF merge, cross-encoder rerank
- LangGraph research agent: retrieve → rerank → generate (stubbed LLM)
- SSE streaming chat: citation events + token events + done event
- JWT authentication: login, token, refresh, protected routes
- PostgreSQL + MinIO + Redis + Qdrant: all running in Docker

### 🔧 Bugs to Fix (T-001 through T-003)
1. `DB_PASS Field required` → fix docker-compose env vars
2. `conversations.tenant_id` missing → run `alembic upgrade head`
3. `python-multipart` missing → add to pyproject.toml, rebuild

### 📋 Next Steps
- Fix bugs, verify everything works (T-001 to T-016)
- Push to GitHub, tag v0.1.0 (T-017 to T-020)
- Begin Stage 2 (real LLM, Telegram, agents)

---

## Architecture (Stage 1)

```
User Browser (Next.js 15, dark dashboard)
    ↕ HTTP/SSE
FastAPI (port 8000)
    ├── PostgreSQL (port 5432) — users, docs, conversations, audit
    ├── Redis (port 6379) — event streams, cache
    ├── Qdrant (port 6333) — vector embeddings
    └── MinIO (port 9000) — document storage

LangGraph Research Agent (inside FastAPI)
    ├── retrieve_docs node → Qdrant hybrid search
    ├── rerank_results node → cross-encoder
    └── generate_answer node → stubbed (no LLM key needed)
```

---

## Growth Stages

| Stage | Services | Goal | Timeline |
|-------|----------|------|----------|
| 1 | 6 | Working chatbot, v0.1.0 | This week |
| 2 | 8 (+ollama, litellm) | Real LLM + Telegram + Upwork | Month 2 |
| 3 | 12 (+browserless, vault, llm-guard, communication) | Revenue | Month 3-4 |
| 4 | Per trigger | Full v5.3 when needed | Month 5+ |

**Philosophy:** Add complexity only when you feel the specific pain of not having it.

---

## Critical Constraints (Memorize These)

| # | Constraint |
|---|-----------|
| 1 | **Stage discipline** — no services from later stages |
| 2 | **No API keys** — stubbed inference only in Stage 1 |
| 3 | **No backend changes** — unless fixing a named bug |
| 4 | **Complete files** — no placeholders, no TODOs |
| 5 | **Docker hostnames** — use service names, not localhost |
| 6 | **ARQ not Celery** — Stages 1-3 |
| 7 | **PostgreSQL not Neo4j** — Stages 1-3 |
| 8 | **useChat.ts** — never rewrite, only import |

---

## Frontend Design Reference

Dark theme CSS Variables:
```css
--bg-base: #0A0A0F
--bg-surface: #12121A
--bg-elevated: #1A1A26
--border: #2A2A3A
--accent: #2563EB
--status-green: #22C55E
--status-red: #EF4444
--text-primary: #F1F5F9
--text-muted: #475569
```

Sidebar sections: KNOWLEDGE | AUTOMATION | ANALYTICS | SETTINGS
Nav items: 10px uppercase tracking-widest
Active state: `border-l-2 border-accent bg-accent-hover`
Status badges: READY=green, PENDING=amber+pulse, FAILED=red

---

## Multi-Agent Vision (Stage 2+)

```
Employee: "Send the Q4 summary to the finance team"
    ↓
Orchestrator Agent decomposes task
    ↓
Research Agent → searches knowledge base for Q4 data
    ↓
Analytics Agent → synthesizes into formatted report
    ↓
Communication Agent → drafts the email
    ↓
LangGraph interrupt() ← ALL AGENTS PAUSE
    ↓
HITL Inbox: Manager sees draft + evidence pack
    ↓
Manager approves (via Telegram /approve)
    ↓
Communication service → email sent
    ↓
Immutable audit log created.
```

**Agents (built in stages):**
- Research Agent ✅ (Stage 1 — read only)
- Lead Scout (Stage 2)
- Proposal Writer (Stage 3)
- Outreach Manager (Stage 3)
- Client Communicator (Stage 3)
- Project Tracker (Stage 3)
- Finance Manager (Stage 3)
- Research Agent v1 (Stage 3)
- Developer Agent (Stage 3, optional)

---

## Environment Variables

### `infrastructure/docker/.env`
```env
DB_PASS=cooppassword123
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
SECRET_KEY=super-secret-key-change-in-production-min-32-chars
ENVIRONMENT=development
```

### `apps/web/.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Test Credentials
```
Admin user:   admin@co-op.local / testpass123
Default tenant: co-op (auto-created on startup)
```

---

## When AI IDE Should Ask vs Just Do

**Just do it:** Bug fixes, missing packages, TypeScript errors, env vars, interfaces.

**Ask first:** Table drops, RAG logic, auth changes, useChat.ts, new Docker services, major deps.

**Never without instruction:** Delete data, change Qdrant schema, add LLM API keys, jump stages.

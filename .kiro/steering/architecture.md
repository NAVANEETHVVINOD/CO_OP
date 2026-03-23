---
inclusion: auto
---

# Co-Op Architecture Reference

## File Structure Map

### Monorepo Root
```
co-op/
├── apps/web/                   # Next.js 16 frontend
├── services/api/               # FastAPI backend (COMPLETE ✅)
├── infrastructure/docker/      # Docker Compose + env config
├── packages/                   # Shared packages (empty Phase 0)
├── docs/                       # Engineering documentation
├── turbo.json                  # Turborepo config
├── pnpm-workspace.yaml         # pnpm workspace config
├── package.json                # Root package.json
└── .env                        # Root env (sync with docker/.env)
```

### Frontend Structure: `apps/web/src/`
```
apps/web/src/
├── app/
│   ├── (app)/                  # Authenticated routes
│   │   ├── layout.tsx          # Auth guard + Sidebar + TopBar
│   │   ├── dashboard/page.tsx  # Stats + health snapshot
│   │   ├── chat/
│   │   │   ├── page.tsx        # Chat interface wrapper
│   │   │   └── ChatPage.tsx    # Client component for chat
│   │   ├── documents/page.tsx  # Document library + upload
│   │   ├── search/page.tsx     # Knowledge search
│   │   ├── agents/page.tsx     # Agent monitor
│   │   ├── approvals/page.tsx  # HITL inbox (empty state Phase 0)
│   │   └── admin/page.tsx      # Admin panel
│   ├── (auth)/
│   │   ├── login/page.tsx      # Login form → POST /v1/auth/token
│   │   └── signup/page.tsx     # Signup form
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Redirect: token? /dashboard : /login
│   └── globals.css             # CSS variables + dark theme
│
├── components/
│   ├── layout/
│   │   ├── AppSidebar.tsx      # Left navigation (240px fixed)
│   │   └── TopBar.tsx          # Header with health indicator
│   ├── shared/
│   │   ├── StatusDot.tsx       # Green/red pulsing dot
│   │   ├── MonoId.tsx          # Truncated UUID with copy
│   │   ├── StatusBadge.tsx     # READY/PENDING/FAILED pill
│   │   ├── EmptyState.tsx      # Centered empty state
│   │   └── PageHeader.tsx      # Page title area
│   └── ui/                     # shadcn/ui components
│
├── hooks/
│   └── useChat.ts              # SSE streaming hook (DO NOT TOUCH ✅)
│
├── lib/
│   ├── api.ts                  # Typed API client (apiFetch wrapper)
│   └── utils.ts                # cn() and helpers
│
├── store/
│   └── chatStore.ts            # Zustand: conversations + messages
│
└── types/
    └── api.ts                  # TypeScript interfaces for all API responses
```

### Backend Structure: `services/api/app/`
```
services/api/
├── main.py                     # FastAPI app factory, lifespan, CORS
├── config.py                   # Pydantic Settings (env-based)
├── dependencies.py             # get_db, get_current_user
│
├── routers/
│   ├── auth.py                 # POST /v1/auth/token, refresh, me
│   ├── chat.py                 # POST /v1/chat/stream (SSE)
│   ├── conversations.py        # GET /v1/chat/conversations
│   ├── documents.py            # POST/GET/DELETE /v1/documents
│   ├── search.py               # POST /v1/search
│   ├── health.py               # GET /health, /ready, /metrics
│   └── approvals.py            # GET/POST /v1/approvals (stub)
│
├── agent/
│   ├── graph.py                # LangGraph StateGraph
│   ├── nodes.py                # retrieve, rerank, generate nodes
│   └── state.py                # AgentState TypedDict
│
├── core/
│   ├── embedder.py             # all-MiniLM-L6-v2 wrapper
│   ├── minio_client.py         # MinIO upload/download
│   ├── redis_client.py         # Redis connection
│   ├── security.py             # JWT encode/decode
│   └── logging.py              # Structured logging
│
├── db/
│   ├── models.py               # SQLAlchemy ORM models
│   ├── repositories.py         # Repository pattern
│   ├── session.py              # Async engine + session
│   └── qdrant_client.py        # Qdrant async client
│
├── events/
│   └── consumer.py             # Redis Streams XREADGROUP consumer
│
├── services/
│   ├── parser.py               # PDF/DOCX/TXT parsing
│   ├── chunker.py              # 512-token chunking
│   ├── embedder.py             # Batch embedding
│   ├── indexer.py              # Qdrant upsert
│   ├── search.py               # Hybrid BM25+dense search
│   ├── reranker.py             # Cross-encoder reranker
│   └── bm25_encoder.py         # BM25 sparse vector encoder
│
└── alembic/
    └── versions/               # Database migrations
```

## API Endpoints (All Working ✅)

### Authentication
```
POST /v1/auth/token
  Body: username=email&password=pass (form-urlencoded, NOT JSON)
  Returns: { access_token, token_type, expires_in }

POST /v1/auth/refresh
  Header: Authorization: Bearer <refresh_token>
  Returns: { access_token }

GET /v1/auth/me
  Header: Authorization: Bearer <token>
  Returns: { id, email, role, tenant_id }
```

### Documents
```
POST /v1/documents
  Header: Authorization: Bearer <token>
  Body: multipart/form-data, file field
  Returns: { id, filename, status: "PENDING" }

GET /v1/documents
  Returns: [{ id, filename, file_type, status, chunk_count, created_at }]

GET /v1/documents/{id}/status
  Returns: { id, status, chunk_count }
  Status: PENDING → INDEXING → READY | FAILED

DELETE /v1/documents/{id}
  Returns: 204 No Content
```

### Chat (SSE Streaming)
```
POST /v1/chat/stream
  Body: { message: str, conversation_id?: str }
  Returns: text/event-stream

  SSE Events:
    event: citation
    data: {"source": "file.pdf", "page": 4, "score": 0.94}

    event: token
    data: {"content": "The policy states..."}

    event: done
    data: {"conversation_id": "uuid", "cost_usd": 0}
```

### Conversations
```
GET /v1/chat/conversations
  Returns: [{ id, title, created_at, message_count? }]

GET /v1/chat/conversations/{id}/messages
  Returns: [{ id, role, content, citations, created_at }]
```

### Search
```
POST /v1/search
  Body: { query: str, top_k?: int, alpha?: float }
  Returns: {
    results: [{
      content, score, source_file,
      page_number, document_id
    }],
    total, latency_ms
  }
```

### Health
```
GET /health
  Returns: {
    status: "ok",
    postgres: "ok"|"error",
    redis: "ok"|"error",
    qdrant: "ok"|"error"
  }

GET /ready
  Returns: 200 if all healthy, 503 if any down

GET /metrics
  Returns: Prometheus text format
```

## Database Schema (PostgreSQL)

### Core Tables
```sql
-- users
id UUID PK
email VARCHAR UNIQUE
role VARCHAR (admin|manager|agent_operator|analyst|viewer)
tenant_id UUID FK
is_active BOOL

-- tenants
id UUID PK
name VARCHAR
slug VARCHAR UNIQUE
plan VARCHAR (community|enterprise)
settings JSONB

-- documents
id UUID PK
tenant_id UUID FK
uploaded_by UUID FK
filename VARCHAR
file_type VARCHAR
status VARCHAR (PENDING|INDEXING|READY|FAILED)
chunk_count INT
minio_key VARCHAR
metadata JSONB

-- conversations
id UUID PK
tenant_id UUID FK
user_id UUID FK
title VARCHAR
created_at TIMESTAMPTZ

-- messages
id UUID PK
conversation_id UUID FK
role VARCHAR (user|assistant)
content TEXT
citations JSONB
created_at TIMESTAMPTZ

-- agent_runs
id UUID PK
agent_type VARCHAR
status VARCHAR (running|completed|failed)
input_payload JSONB
output_payload JSONB
token_cost_usd DECIMAL

-- hitl_approvals (Phase 2)
id UUID PK
agent_run_id UUID FK
proposed_action JSONB
status VARCHAR (pending|approved|rejected)

-- audit_events (append-only)
id BIGSERIAL PK
event_type VARCHAR
user_id UUID
payload JSONB
created_at TIMESTAMPTZ

-- cost_events
id BIGSERIAL PK
model_id VARCHAR
input_tokens INT
output_tokens INT
cost_usd DECIMAL
```

### Current Alembic State
Latest migration: `14e1dfdf2a5b_add_tenant_id_to_conversations.py`

Run migrations: `cd services/api && alembic upgrade head`

## Docker Services & Ports

| Service | Port | Internal URL | External URL |
|---------|------|--------------|--------------|
| co-op-api | 8000 | http://co-op-api:8000 | http://localhost:8000 |
| co-op-web | 3000 | http://co-op-web:3000 | http://localhost:3000 |
| postgres | 5432 | postgres:5432 | localhost:5433 |
| redis | 6379 | redis:6379 | localhost:6379 |
| qdrant | 6333 | http://qdrant:6333 | http://localhost:6333 |
| minio (API) | 9000 | minio:9000 | http://localhost:9000 |
| minio (Console) | 9001 | N/A | http://localhost:9001 |

**Inside Docker:** Use service names (postgres, redis, qdrant, minio)
**From host machine:** Use localhost with mapped ports

## TypeScript API Types

Located in `apps/web/src/types/api.ts`:

```typescript
interface Document {
  id: string
  filename: string
  file_type: string
  file_size: number
  status: 'PENDING' | 'INDEXING' | 'READY' | 'FAILED'
  chunk_count: number
  created_at: string
  error_message?: string
}

interface Conversation {
  id: string
  title: string
  message_count?: number
  created_at: string
}

interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  citations: Citation[]
  created_at: string
}

interface Citation {
  source: string
  page: number
  score: number
  content?: string
}

interface SearchResult {
  document_id: string
  text: string
  score: number
  source_file: string
  page_number: number
}

interface HealthResponse {
  status: string
  postgres: string
  redis: string
  qdrant: string
  minio?: string
}
```

## Design System (Dark Theme)

CSS Variables in `apps/web/src/app/globals.css`:

```css
--bg-base: #0A0A0F        /* page background */
--bg-surface: #12121A     /* cards, sidebar */
--bg-elevated: #1A1A26    /* hover states, inputs */
--border: #2A2A3A         /* subtle borders */
--border-bright: #3A3A50  /* hover borders */
--accent: #2563EB         /* primary blue */
--status-green: #22C55E
--status-red: #EF4444
--status-amber: #F59E0B
--text-primary: #F1F5F9
--text-secondary: #94A3B8
--text-muted: #475569
```

### UI Patterns
- Section headers: `10px, uppercase, tracking-widest, text-muted`
- Monospace IDs: `JetBrains Mono, text-muted, truncated to 8 chars`
- Active nav item: `border-l-2 border-accent bg-accent-hover`
- Status badges: READY=green, PENDING=amber+pulse, FAILED=red

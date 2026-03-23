# Co-Op — Autonomous Company OS

> Self-hosted AI platform that runs your freelance business.
> Agents find clients, write proposals, communicate, track projects, and invoice — with your approval on every important action.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

## What Is Co-Op?

Co-Op is an **autonomous company operating system** built for solo developers. Deploy it on your own machine and let AI agents handle the repetitive work of freelancing:

- **Find clients** — Lead Scout scans job boards every 4 hours
- **Write proposals** — Proposal Writer crafts personalized responses using your portfolio
- **Communicate** — Client Communicator handles professional email exchanges
- **Track projects** — Project Tracker sets milestones and deadline alerts
- **Create invoices** — Finance Manager generates invoices from completed milestones
- **You stay in control** — Human approval required for every important action via Telegram or dashboard

**Comparable to:** Microsoft Copilot + Glean AI + Zapier — but self-hosted and open source.

---

## How It Grows (4 Stages)

Co-Op follows a staged architecture. Start small and add complexity only when you feel the pain.

| Stage | Services | What You Get | Timeline |
|-------|----------|-------------|----------|
| **1** | 6 | Working chatbot with document RAG | This week |
| **2** | 8 | Real LLM + Telegram control + Upwork reading | Month 2 |
| **3** | 12 | Proposals submitted, client communication, first revenue | Month 3-4 |
| **4** | Per trigger | Enterprise components when needed | Month 5+ |

---

## Quick Start (Stage 1)

### Prerequisites
- Docker Desktop (4GB+ RAM)
- Node.js 18+ with pnpm
- Git

### 1. Clone and Configure

```bash
git clone https://github.com/NAVANEETHVVINOD/CO_OP.git
cd CO_OP

# Create environment files
cp infrastructure/docker/.env.example infrastructure/docker/.env
cp apps/web/.env.example apps/web/.env.local
```

### 2. Start Services

```bash
cd infrastructure/docker
docker compose up -d
```

### 3. Verify

```bash
# All 6 containers should be healthy
docker compose ps

# Backend health check
curl http://localhost:8000/health

# Frontend
cd ../../apps/web
pnpm install
pnpm dev
```

### 4. Login

Open http://localhost:3000 and login with:
```
Email:    admin@co-op.local
Password: testpass123
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, CSS Variables, Zustand, TanStack Query |
| Backend | FastAPI, async SQLAlchemy, Alembic |
| AI/Agents | LangGraph, LiteLLM (Ollama in Stage 2) |
| Knowledge | Qdrant (384-dim), all-MiniLM-L6-v2 |
| Background Tasks | ARQ (Stages 1-3), Temporal (Stage 4) |
| Storage | PostgreSQL 16, MinIO S3, Redis |
| Deployment | Docker Compose |

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Next.js 15 Dashboard            │
│      (Dark theme, SSE streaming)        │
└────────────────┬────────────────────────┘
                 │ HTTP/SSE
┌────────────────▼────────────────────────┐
│           FastAPI Backend               │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌───────┐  │
│  │ Auth │ │ Chat │ │ Docs │ │Search │  │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬────┘  │
│     │     ┌──▼───────────────┐  │       │
│     │     │ LangGraph Agent  │  │       │
│     │     │ retrieve→rerank  │  │       │
│     │     │ →generate        │  │       │
│     │     └──────────────────┘  │       │
└─────┼────────────────────────┼──┼───────┘
      │                        │  │
┌─────▼──┐ ┌────────┐ ┌──────▼┐ ┌▼─────┐
│Postgres│ │ Redis  │ │Qdrant │ │MinIO │
│  5432  │ │  6379  │ │ 6333  │ │ 9000 │
└────────┘ └────────┘ └───────┘ └──────┘
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [Architecture Blueprint](docs/CO_OP_SOLO_DEVELOPER_ARCHITECTURE.md) | Full staged architecture |
| [Task List](docs/CO_OP_SOLO_TASKS_UPDATED.md) | 83 tasks across 4 stages |
| [Stage 1 Guide](docs/stage1_implementation.md) | Foundation setup |
| [Stage 2 Guide](docs/stage2_implementation.md) | LLM + Telegram |
| [Stage 3 Guide](docs/stage3_implementation.md) | Agents + Revenue |
| [Stage 4 Guide](docs/stage4_implementation.md) | Scaling triggers |
| [Project Reference](docs/PROJECT.md) | Master reference |

---

## Contributing

This project follows the solo developer philosophy documented in `docs/rules/co-op-solo-guidelines.mdc`. Before contributing:

1. Read `docs/PROJECT.md` — understand the project's current state
2. Read `docs/rules/co-op-critical-constraints.mdc` — understand what's forbidden
3. Check the stage — don't add enterprise components to earlier stages
4. Follow coding standards in `docs/rules/co-op-coding-standards.mdc`

---

## License

Apache License 2.0 — See [LICENSE](LICENSE)

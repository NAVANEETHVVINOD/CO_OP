# Co-Op Solo Developer Edition
# Architecture for a Solo Developer with AI IDE (Kiro/Cursor)
# Start small. Earn money. Scale when needed.

---

## THE HONEST REALITY CHECK

Multiple expert reviews agreed on one thing:
v5.3 is the CORRECT long-term architecture.
But starting with 29 services as a solo developer is a trap.

You will spend month 1 fixing Docker networking.
You will spend month 2 debugging Temporal.
You will spend month 3 learning OPA.
You will spend month 4 wondering why you have not shipped anything.

The right approach:
  6 services → earn first money → add services when you need them.
  
This document gives you a clean path from 6 services to the full
v5.3 architecture at exactly the right pace.

You have AI IDEs (Kiro/Antigravity). That is a massive advantage.
Use them to build one phase at a time, not to scaffold 29 services at once.

---

## THE SOLO ARCHITECTURE — 4 GROWTH STAGES

```
STAGE 1 (Week 1):     6 services — Company GPT. Talking chatbot.
STAGE 2 (Month 2):    8 services — Real AI. Telegram. Lead Search.
STAGE 3 (Month 3-4): 12 services — Agents proposing and communicating.
STAGE 4 (Month 5+):  Full v5.3 — When revenue justifies complexity.
```

Never add a service unless you feel the pain of not having it.

---

# STAGE 1 — THE FOUNDATION
# 6 Services | This Week | Goal: Working chatbot you can show people

```
co-op-api       (8000)  FastAPI — handles all requests
co-op-web       (3000)  Next.js — the dashboard you interact with
postgres        (5432)  PostgreSQL — all data lives here
redis           (6379)  Redis — caching, task queues, hot memory
qdrant          (6333)  Qdrant — vector search for documents
minio           (9000)  MinIO — file storage for uploaded docs
```

What this gives you:
  Upload a PDF → AI answers questions about it
  Login works, dashboard works, search works, chat works
  The full RAG pipeline is functional
  You can demo this to anyone

What it does NOT have yet (and that is fine):
  Real LLM (still stubbed — you need to fix this in Stage 2)
  Telegram connection
  Any real agents
  Any external API calls

STAGE 1 TASKS:
  1. Fix all 3 Phase 0 bugs (docker env vars, migration, multipart)
  2. pnpm build → zero TypeScript errors
  3. Login → dashboard → upload → search → chat works
  4. git push origin main && git tag v0.1.0

---

# STAGE 2 — REAL INTELLIGENCE
# 8 Services | Month 2 | Goal: Real LLM + Telegram control + Upwork reading

Add to Stage 1:
  ollama     (11434) — serves Llama 3.1 8B locally (real LLM responses)
  litellm    (4000)  — budget enforcement + routes to right model

That is it. Just 2 new services.

With just 8 services you get:
  Real LLM responses (not stubbed)
  Per-agent daily token limits enforced
  Hardware detection → recommends right model for your machine
  Telegram bot for /status, /pause, /panic commands
  Thinking display in Telegram as agents work
  System Monitor cron checking health every 5 minutes
  Lead Scout reading Upwork every 4 hours (read-only, no submitting)
  Morning brief at 8am in Telegram

The Telegram bot and Lead Scout run INSIDE the co-op-api service.
No new containers needed. ARQ (async Redis queue) replaces Celery
for background tasks. One line in requirements.txt.

Why ARQ instead of Celery?
  Celery = 400 lines of config, Redis + RabbitMQ options, heavy
  ARQ = asyncio-native, works directly with FastAPI, 0 config
  For 4 agents running on one machine: ARQ is perfect

STAGE 2 TASKS:
  1. Deploy Ollama + pull Llama 3.1 8B
  2. Deploy LiteLLM with budget enforcement
  3. Build Telegram bot (inside co-op-api — no new service)
  4. Build ARQ worker pool (inside co-op-api — no new service)
  5. Hardware Detector (psutil, writes to postgres settings table)
  6. System Monitor cron (every 5 min, Telegram alerts)
  7. Lead Scout agent (Upwork via requests/httpx, no Browserless yet)
  8. Morning Brief cron (8am Telegram message)

---

# STAGE 3 — WORKING AGENTS
# 12 Services | Month 3-4 | Goal: Proposals submitted. Clients talking.

Add to Stage 8:
  browserless   (8030) — headless Chrome for real web scraping
  vault         (8200) — move credentials out of .env
  llm-guard     (8060) — prompt injection protection
  communication (8010) — dedicated service for Telegram/Discord/Email

Why add Browserless now?
  Lead Scout using httpx works until Upwork blocks your IP.
  Browserless handles anti-bot and sessions properly.
  You will feel the pain of not having it after a week of scraping.

Why add Vault now?
  You are about to store Upwork credentials, email tokens, API keys.
  .env files are fine for 2 services. Wrong for 12.

Why add LLM Guard now?
  Agents will soon receive external content (job descriptions,
  client messages). You need to scan inputs before they reach the LLM.

What this stage delivers:
  Proposal Writer generates personalized proposals from your portfolio
  You approve proposals from Telegram (/approve 1 3)
  Outreach Manager submits approved proposals to Upwork
  Client Communicator handles client replies via email
  Finance Manager creates invoices (you approve before sending)
  System Monitor can restart failed services automatically
  Company Profile Builder (conversation wizard in browser)

Architecture notes for Stage 3:
  STILL no Temporal — use ARQ workflows for proposal pipeline
  STILL no NATS — Redis queues are fine at this scale
  STILL no Neo4j — use PostgreSQL JSONB for relationship data
  STILL no OPA — use simple FastAPI role checks
  STILL no microsandbox — Docker sandbox only (no code delivery yet)

STAGE 3 TASKS (Month 3):
  1. Deploy Browserless Docker (domain whitelist configured)
  2. Deploy HashiCorp Vault (migrate all credentials from .env)
  3. Deploy LLM Guard (wrap /v1/chat and /v1/search)
  4. Deploy Communication service (Telegram + Email adapters)
  5. Build Proposal Writer agent (RAG on your portfolio docs)
  6. Build HITL approval system (Telegram /approve command)
  7. Build Outreach Manager (submits via Composio Upwork tool)
  8. Tag v0.2.0

STAGE 3 TASKS (Month 4):
  9. Build Client Communicator agent (email/Telegram replies)
  10. Build Project Tracker (milestones in PostgreSQL)
  11. Build Finance Manager (invoice creation + email sending)
  12. Build Company Profile wizard (browser conversation)
  13. Connect Composio MCP (Gmail + Upwork + LinkedIn)
  14. Simulation mode toggle (fake Upwork jobs for testing)
  15. Tag v0.3.0

---

# STAGE 4 — SCALING TO FULL V5.3
# Add services only when you feel the specific pain
# Month 5 onward

Pain signal → What to add:

"Agents keep getting stuck in loops, I lose $50 before noticing"
→ Add: Temporal + zombie detector

"I want to deliver actual websites and code to clients"
→ Add: code-server + microsandbox + execution sandbox

"I'm running 10 agents and LLM is a bottleneck"
→ Add: vLLM (if you have GPU) or upgrade Groq/Gemini API usage

"I need proper distributed tracing to debug agent behavior"
→ Add: OpenTelemetry + Grafana Tempo + Prometheus

"I have 3 clients and I'm spending 2 hours/week approving things"
→ Add: auto-approval rule engine

"Research Agent keeps proposing changes that break things"
→ Add: shadow environment + microsandbox validation

"I need to run multiple companies / have a team"
→ Add: NATS JetStream + company brain service + full RBAC

"Enterprise client needs SSO and SOC2"
→ Add: Keycloak + OPA + Vault enterprise + Helm charts

You will naturally feel each of these pains at the right time.
Do not add them preemptively.

---

## SERVICE COMPARISON: SOLO VS FULL

| Service | Stage 1 | Stage 2 | Stage 3 | Full v5.3 |
|---------|---------|---------|---------|-----------|
| co-op-api | ✅ | ✅ | ✅ | ✅ |
| co-op-web | ✅ | ✅ | ✅ | ✅ |
| postgres | ✅ | ✅ | ✅ | ✅ |
| redis | ✅ | ✅ | ✅ | ✅ |
| qdrant | ✅ | ✅ | ✅ | ✅ |
| minio | ✅ | ✅ | ✅ | ✅ |
| ollama | — | ✅ | ✅ | ✅ |
| litellm | — | ✅ | ✅ | ✅ |
| browserless | — | — | ✅ | ✅ |
| vault | — | — | ✅ | ✅ |
| llm-guard | — | — | ✅ | ✅ |
| communication | — | — | ✅ | ✅ |
| temporal | — | — | — | Phase 2 |
| nats | — | — | — | Phase 2 |
| neo4j | — | — | — | Phase 2 |
| opa | — | — | — | Phase 2 |
| traefik | — | — | — | Phase 2 |
| microsandbox | — | — | — | Phase 2 |
| code-server | — | — | — | Phase 2 |
| otel/grafana | — | — | — | Phase 2 |
| vllm | — | — | — | Phase 2 GPU |

---

## KEY TECHNOLOGY SIMPLIFICATIONS

### ARQ instead of Celery (Stages 1-3)

```python
# Install: pip install arq
# arq works directly with async FastAPI, no config needed

import arq

async def lead_scout_task(ctx, company_id: str):
    """Runs every 4 hours to find new leads"""
    jobs = await search_upwork(company_id)
    await notify_telegram(f"Found {len(jobs)} leads")

class WorkerSettings:
    functions = [lead_scout_task]
    redis_settings = arq.connections.RedisSettings()
    cron_jobs = [
        arq.cron(lead_scout_task, hour={8, 12, 16, 20}, minute=0)
    ]
```

Replace Celery with arq when you add Stage 2.
Switch to Celery+NATS in Stage 4 if you outgrow arq.

### PostgreSQL JSONB instead of Neo4j (Stages 1-3)

```sql
-- Store client relationships in JSONB, not a graph DB
CREATE TABLE client_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    facts JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Query: what do we know about this client?
SELECT facts FROM client_memory
WHERE tenant_id = $1 AND client_id = $2;

-- Update: client prefers casual tone
UPDATE client_memory
SET facts = facts || '{"tone": "casual", "updated": "2026-03"}'::jsonb
WHERE client_id = $2;
```

Add Neo4j in Stage 4 when you have 50+ clients with complex relationships.

### pgvector instead of separate Qdrant (optional, Stage 1 only)

If you want to save even more RAM in Stage 1:

```sql
-- Add pgvector extension to PostgreSQL
CREATE EXTENSION IF NOT EXISTS vector;

-- Store embeddings in PostgreSQL directly
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL,
    content TEXT,
    embedding vector(384),  -- all-MiniLM-L6-v2 dimensions
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Semantic search with pgvector
SELECT content, 1 - (embedding <=> $1) AS similarity
FROM document_chunks
WHERE 1 - (embedding <=> $1) > 0.7
ORDER BY similarity DESC LIMIT 5;
```

This removes Qdrant entirely in Stage 1 (saves 500MB RAM).
Add Qdrant back in Stage 2 when you have 1000+ document chunks.

Decision guide:
  < 10,000 chunks: pgvector in PostgreSQL (no Qdrant needed)
  > 10,000 chunks: add Qdrant back (better ANN performance)

### FastAPI role checks instead of OPA (Stages 1-3)

```python
# Simple, readable, no config files needed

from enum import Enum
from functools import wraps

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"

def require_role(allowed_roles: list[Role]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage in router
@router.post("/approvals/{id}")
@require_role([Role.ADMIN, Role.MANAGER])
async def approve_action(id: str, current_user: User = Depends()):
    ...
```

Add OPA in Stage 4 when you have 5+ role types and complex policy rules.

### Docker sandbox instead of microsandbox (Stages 1-3)

```python
# Simple Docker sandbox for code execution
import docker

async def run_code_in_sandbox(code: str, language: str) -> str:
    client = docker.from_env()
    container = client.containers.run(
        image=f"coop-sandbox-{language}:latest",
        command=["sh", "-c", code],
        mem_limit="512m",
        cpu_quota=50000,           # 50% of one CPU
        network_disabled=True,     # No internet
        remove=True,               # Destroy after run
        timeout=30,
        read_only=True,            # Read-only filesystem
        security_opt=["no-new-privileges:true"]
    )
    return container.decode("utf-8")
```

This is secure enough for your own use.
Add microsandbox (microVMs) in Stage 4 when you accept
code submissions from external clients or untrusted sources.

---

## HARDWARE REQUIREMENTS PER STAGE

### Stage 1 (6 services):
  RAM: 4GB minimum, 8GB comfortable
  CPU: Any dual-core
  Disk: 10GB
  Cost: Your own laptop or Hetzner CX11 (€3/month)

### Stage 2 (8 services + Ollama):
  RAM: 8GB minimum (Llama 3.1 8B needs ~5GB)
  CPU: 4+ cores recommended
  Disk: 20GB (model files)
  Cost: Hetzner CX21 (8GB RAM, €5/month) or your laptop

### Stage 3 (12 services):
  RAM: 16GB recommended
  CPU: 4+ cores
  Disk: 30GB
  Cost: Hetzner CX31 (16GB RAM, €9/month) or workstation
  Note: Can still run on 8GB with careful config (disable observability)

### Stage 4 (Full v5.3):
  RAM: 32GB+ (64GB for GPU inference)
  CPU: 8+ cores
  Disk: 100GB+
  Cost: Hetzner AX42 (64GB, €55/month) or dedicated server

---

## FULL TASK LIST — SOLO DEVELOPER EDITION

══════════════════════════════════════════════════════════
STAGE 1 — FOUNDATION (This Week)
══════════════════════════════════════════════════════════

- [ ] **Fix Docker env vars**
  Add DB_PASS, DATABASE_URL, REDIS_URL, QDRANT_URL, MINIO_ENDPOINT,
  SECRET_KEY, ENVIRONMENT, PYTHONPATH to co-op-api service in
  docker-compose.yml. The API crashes without these.
  Done when: docker compose up → API starts without "Field required" error

- [ ] **Run Alembic migration**
  The conversations table is missing the tenant_id column.
  Run: cd services/api && alembic upgrade head
  Done when: curl /v1/chat/conversations returns [] not 500 error

- [ ] **Add python-multipart dependency**
  The login endpoint needs this library to parse form data.
  Add to pyproject.toml: "python-multipart>=0.0.9"
  Rebuild: docker compose build co-op-api
  Done when: POST /v1/auth/token returns a JWT token

- [ ] **Verify all 6 services healthy**
  Run: docker compose ps → all 6 show Up (healthy)
  Run: curl localhost:8000/health → all services ok
  Done when: health endpoint returns all green

- [ ] **Fix TypeScript build errors**
  Run: cd apps/web && pnpm build
  Fix every error in the output. Common issues: missing imports,
  wrong types, undefined components.
  Done when: pnpm build exits code 0

- [ ] **Test the complete user flow**
  Login → dashboard → upload PDF → wait for READY status →
  search query → get results → chat question → streaming answer
  Done when: all steps complete without errors

- [ ] **Check browser console is clean**
  Open DevTools Console while clicking through all pages.
  Done when: zero red errors in console

- [ ] **Set up .gitignore correctly**
  Verify .env, .venv, node_modules, .next are all excluded.
  Run: git status → no sensitive files shown as untracked
  Done when: git status is clean

- [ ] **Push to GitHub and tag v0.1.0**
  Run: git add . && git commit -m "feat: Phase 0 complete"
       git push origin main
       git tag v0.1.0 && git push origin v0.1.0
  Done when: commit and tag visible on GitHub

══════════════════════════════════════════════════════════
STAGE 2 — REAL INTELLIGENCE (Month 2, Weeks 1-4)
══════════════════════════════════════════════════════════

WEEK 1 — Local LLM

- [ ] **Add Ollama to docker-compose.yml**
  Add the ollama service with port 11434. Mount a volume for
  model storage so models survive container restarts.
  Done when: ollama responds at localhost:11434

- [ ] **Pull Llama 3.1 8B model**
  Run: docker exec ollama ollama pull llama3.1:8b
  This downloads ~5GB. Also pull llama3.2:3b for simple tasks.
  Done when: both models available, test query returns real response

- [ ] **Add LiteLLM to docker-compose.yml**
  Configure litellm_config.yaml to route:
  simple tasks → llama3.2:3b, standard → llama3.1:8b
  Set per-agent daily token limits in config.
  Done when: LiteLLM responds, routes tasks to correct model

- [ ] **Build Hardware Detector**
  Use psutil + py-cpuinfo in a startup script. Reads RAM and
  GPU, assigns SOLO/TEAM/AGENCY tier, writes to postgres settings.
  Shows hardware info in dashboard header.
  Done when: coop doctor shows correct hardware tier

- [ ] **Replace stubbed inference with real LLM**
  Update the LangGraph generate_answer node to call LiteLLM
  instead of returning placeholder text.
  Done when: chat returns real LLM-generated answers using document context

WEEK 2 — ARQ Workers

- [ ] **Add arq to pyproject.toml**
  Install: "arq>=0.25"
  Create services/api/app/worker.py with WorkerSettings class.
  ARQ runs as a second process inside the co-op-api container
  (not a separate container).
  Done when: background tasks execute asynchronously

- [ ] **Build System Monitor cron with ARQ**
  Cron every 5 minutes: check all Docker containers, API health,
  Redis queue depth. Attempt self-heal on failure. Alert Telegram.
  Done when: stop a container → Telegram alert within 60 seconds

- [ ] **Add arq to docker-compose startup command**
  Update co-op-api Dockerfile entrypoint to run both
  uvicorn (API) and arq worker in the same container using
  a process supervisor (supervisord or a simple shell script).
  Done when: both API and background workers run from one container

WEEK 3 — Telegram Bot

- [ ] **Build Telegram bot (inside co-op-api)**
  Add python-telegram-bot to dependencies. Create a Telegram
  adapter that runs as an arq background task. No separate
  container needed.
  Done when: /start command returns system status

- [ ] **Implement all Telegram commands**
  /status, /pause, /resume, /panic, /approve [n], /budget, /help
  Done when: each command triggers correct system action

- [ ] **Build thinking display (numbered progress steps)**
  As arq tasks run, publish progress to Redis channel.
  Telegram bot subscribes and sends numbered step updates.
  Done when: running a task shows live numbered steps in Telegram

- [ ] **Build credit tracker widget in dashboard**
  Read token usage from LiteLLM callback logs in PostgreSQL.
  Show live bar: green (normal), amber (80%), red (95%+).
  Done when: dashboard shows real token usage updating live

WEEK 4 — First Agent

- [ ] **Add KVM check to startup**
  In the API startup, check if /dev/kvm exists. Write sandbox_tier
  (microsandbox/gvisor/docker) to PostgreSQL settings. Show warning
  in dashboard and coop doctor output if not TIER 1.
  Done when: coop doctor shows sandbox tier with appropriate message

- [ ] **Build Company Profile wizard**
  8-question browser conversation. Store profile in PostgreSQL
  as company_profiles table. Index key facts in Qdrant (or pgvector).
  Done when: wizard completes → profile visible in dashboard

- [ ] **Build Lead Scout agent (reads Upwork)**
  Uses httpx (not Browserless yet) to call Upwork's API or search
  page. Scores jobs against company profile (0-10). Reports top 5
  to Telegram with thinking display. READ-ONLY — no submissions.
  Run every 4 hours via ARQ cron.
  Done when: Lead Scout sends Telegram message with real job findings

- [ ] **Build Morning Brief cron**
  8am daily ARQ cron. Telegram message: overnight activity,
  new leads, system health, token usage vs budget.
  Done when: 8am message received with accurate data

- [ ] **Set up daily backup**
  Simple shell script: pg_dump, qdrant snapshot, minio sync.
  Run daily at 2am via ARQ cron. Alert Telegram on failure.
  Done when: backup runs, test restore works from backup files

- [ ] **Tag v0.2.0**
  Done when: commit and tag pushed to GitHub

══════════════════════════════════════════════════════════
STAGE 3 — WORKING AGENTS (Months 3-4)
══════════════════════════════════════════════════════════

MONTH 3

- [ ] **Deploy Browserless Docker**
  Add browserless/chrome to docker-compose. Configure domain
  whitelist. Update Lead Scout to use Browserless instead of httpx.
  Done when: Lead Scout scrapes real Upwork job listings via Browserless

- [ ] **Deploy HashiCorp Vault**
  Move all credentials from .env to Vault. Update services to
  request credentials from Vault at startup.
  Done when: zero secrets in .env, all retrieved from Vault

- [ ] **Deploy LLM Guard**
  Add llm-guard to docker-compose. Wrap /v1/chat and /v1/search.
  Log all blocked requests to audit_events.
  Done when: prompt injection attempt returns 400 with reason

- [ ] **Deploy Communication service**
  Dedicated FastAPI service for all messaging platforms.
  Telegram adapter migrated from co-op-api to this service.
  Email adapter added (SMTP + Gmail API).
  Done when: Telegram and email both work through communication service

- [ ] **Build Proposal Writer agent**
  RAG on portfolio documents in Qdrant. Drafts under 200 words.
  Self-reviews (specific? references the job? under word limit?)
  Sends to HITL queue. Telegram: "3 proposals ready — /approve 1 2 3"
  Done when: real Upwork job → personalized proposal → HITL queue

- [ ] **Build HITL approval system**
  Risk levels: READ-ONLY (auto), LOW (auto+notify), MEDIUM (24h
  then reject), HIGH (24h then reject), CRITICAL (wait forever).
  Approve from Telegram or dashboard.
  Done when: proposal appears in approval inbox, /approve submits it

- [ ] **Connect Composio MCP (Gmail + Upwork)**
  OAuth tokens stored in Vault. Outreach Manager uses these to
  submit approved proposals to Upwork and send follow-up emails.
  Done when: approved proposal → submitted to real Upwork job

- [ ] **Build auto-approval rule engine**
  YAML config: which action types auto-approve after N successful uses.
  Never auto-approve: proposals, invoices, payments.
  Done when: follow-up email #4 auto-approves based on config

- [ ] **Tag v0.3.0**

MONTH 4

- [ ] **Build Client Communicator agent**
  Handles incoming client messages via email. Professional tone.
  Never claims to be human if asked. Escalates to HITL for complaints
  and scope changes. Saves conversation history to PostgreSQL JSONB.
  Done when: client email received → agent responds professionally

- [ ] **Build Project Tracker agent**
  Creates milestones from project requirements. Deadline alerts
  72 hours before each milestone. Status updates to client
  (human approves before sending).
  Done when: project created → milestones set → reminder received

- [ ] **Build Finance Manager agent**
  Creates invoices from project milestones. Human approves before
  sending. 7-day payment reminder workflow using ARQ.
  Done when: project delivered → invoice created → sent to client

- [ ] **Add Simulation Mode**
  Dashboard [Live] ↔ [Simulation] toggle. Fake Upwork jobs,
  fake client personas, all sends intercepted. Metrics tracked
  identically to production.
  Done when: simulation mode works, fake jobs appear in Lead Scout

- [ ] **Build client portal (Phase 3 preview)**
  Simple read-only page for clients. HMAC URL, no login needed.
  Shows project status, milestones, next steps.
  Done when: client receives URL and sees project status page

- [ ] **Set up prompt CI/CD**
  GitHub Actions: runs DeepEval on any PR touching prompts.
  Fails CI if win rate drops or injection passes.
  Done when: PR with prompt change → CI posts evaluation results

- [ ] **Build Research Agent v1**
  Scans GitHub Trending and HuggingFace weekly. Scores relevance.
  If > 7/10: runs micro-benchmark in Docker sandbox.
  Proposes to human with benchmark result.
  Done when: weekly Telegram message with a real discovery and test results

- [ ] **Full end-to-end test**
  Lead finds job → proposal approved → submitted → client replies
  → agent responds → project tracked → invoice created.
  Done when: first real project earned through the system

- [ ] **Tag v0.4.0 — First Revenue Version**

══════════════════════════════════════════════════════════
STAGE 4 — WHEN TO ADD FULL V5.3 COMPONENTS
══════════════════════════════════════════════════════════

Add these only when you feel the specific pain.
Each item below has a "trigger" — the event that tells you it is time.

TRIGGER: "ARQ loses tasks when the container restarts mid-workflow"
→ Add Temporal (durable workflow engine, port 7233)

TRIGGER: "Agents burn money in infinite loops before I notice"
→ Add Zombie detector + Temporal (zombie detection needs Temporal)

TRIGGER: "I'm delivering actual code to clients but Docker sandbox
          feels unsafe — client submitted suspicious code"
→ Add microsandbox (microVM isolation, requires KVM)

TRIGGER: "Code tasks take forever because npm/pip downloads are slow"
→ Add Verdaccio (npm mirror) + devpi (PyPI mirror)

TRIGGER: "I have 10 agents and the LLM is a bottleneck at peak hours"
→ Add vLLM (needs GPU) OR upgrade to Groq/Gemini paid API

TRIGGER: "I can't figure out why an agent did what it did last Tuesday"
→ Add OpenTelemetry + Grafana Tempo (distributed tracing)

TRIGGER: "I have a team of 3 people and need role-based access"
→ Add OPA (Open Policy Agent) + proper RBAC

TRIGGER: "Clients asking their messages go through AI is a concern"
→ Add NATS JetStream (better message reliability at scale)

TRIGGER: "I want to understand patterns across all my clients"
→ Add Neo4j + Graphiti (replaces PostgreSQL JSONB for graph data)

TRIGGER: "Enterprise client wants SSO with their Google Workspace"
→ Add Keycloak (OIDC/SAML integration)

TRIGGER: "Second server required for reliability"
→ Add Traefik + Docker Swarm (multi-node deployment)

TRIGGER: "10+ companies running on my platform, I need isolation"
→ Add full NATS + company-brain-service + agent-runtime-service

---

## YOUR DOCKER COMPOSE EVOLUTION

### Stage 1 (6 services) — docker-compose.yml
```
services: api, web, postgres, redis, qdrant, minio
```

### Stage 2 (8 services) — add to existing
```
+ ollama
+ litellm
```

### Stage 3 (12 services) — add to existing
```
+ browserless
+ vault
+ llm-guard
+ communication
```

### Stage 4 (add per trigger, not all at once)
```
+ temporal         (when ARQ isn't durable enough)
+ microsandbox     (when you need microVM isolation)
+ neo4j            (when JSONB graph queries are too slow)
+ opa              (when role logic gets complex)
+ nats             (when Redis queue isn't distributed enough)
+ otel-collector   (when you need proper distributed tracing)
+ grafana-tempo    (with otel-collector)
+ vllm             (when GPU available and throughput needed)
+ verdaccio        (when sandbox startup speed matters)
+ devpi            (with verdaccio)
+ traefik          (when going multi-node)
+ company-brain    (when multi-company needed)
+ agent-runtime    (when separating agent execution matters)
+ shadow-postgres  (when self-improvement A/B testing needed)
```

---

## REALISTIC REVENUE TIMELINE

Month 1 (Stage 1-2):
  System works. Real LLM responses. Can demo to people.
  Lead Scout reading Upwork. You are reviewing leads manually.
  Revenue: £0 (building)

Month 2 (Stage 2 complete):
  Telegram connected. Morning brief working.
  You see leads every morning and can manually propose.
  Revenue: First proposals going out. Possible first £500-1000.

Month 3 (Stage 3 start):
  Proposal Writer drafting proposals automatically.
  You are reviewing and approving, not writing.
  Revenue: £500-2000/month possible if win rate is decent.

Month 4 (Stage 3 complete):
  Clients communicating with your agent.
  Projects being tracked. Invoices being sent.
  Revenue: £1000-5000/month is achievable.

Month 5+ (as needed):
  Scale the parts that are actually bottlenecks.
  Revenue: Limited by your capacity to deliver, not the system.

The system can earn money with just 12 services.
Everything after that is optimization.

---

## HOW TO USE YOUR AI IDE (KIRO/ANTIGRAVITY) EFFECTIVELY

Your AI IDE is your biggest advantage as a solo developer.
Here is how to use it right for this project:

ONE TASK AT A TIME:
  Give Kiro/Antigravity one specific task from this list.
  "Build the ARQ worker that runs Lead Scout every 4 hours"
  Not: "Build the entire Stage 2 agent system"

PROVIDE CONTEXT FILES:
  Before starting any task, point the AI to these files:
  - services/api/app/main.py (entry point)
  - services/api/app/config.py (all settings)
  - services/api/app/db/models.py (database schema)
  - infrastructure/docker/docker-compose.yml (services)
  - This architecture document

USE THE ARCHITECTURE AS YOUR SPEC:
  The task descriptions in this document are your spec.
  Paste the task description plus the "Done when" criteria
  into your AI IDE as the goal.

VERIFY BEFORE MOVING ON:
  Each task has a "Done when" statement.
  Run that verification before starting the next task.
  Do not trust "code looks good" — run the actual check.

DO NOT LET THE AI OVER-ENGINEER:
  If the AI suggests adding Temporal or NATS during Stage 1-3,
  refuse. Tell it: "We are in Stage 3 of a solo architecture.
  Use ARQ instead of Celery, PostgreSQL JSONB instead of Neo4j,
  FastAPI role checks instead of OPA."

---

## THE ONE RULE

Start with the minimum that works.
Add complexity only when you feel a specific pain.
Ship early. Get real users. Let their needs drive what to build next.

You have the full v5.3 architecture as the destination.
You do not need to arrive there on day one.
You need to arrive there one step at a time, earning money along the way.

# Co-Op Solo Developer — Updated Task List
# 4 Stages | ~4 months to first revenue
# Last updated: 2026-03-23

---

## HOW TO USE THIS LIST

- Work top to bottom, never skip ahead
- Each task has: **what to do** + **why it matters** + **Done when**
- The "Done when" step is mandatory — run the actual check before moving on
- Mark `[x]` when complete, `[/]` when in progress
- If a task blocks you for more than 2 hours, ask your AI IDE for help
- Tasks marked **(optional)** can be skipped without blocking later stages

---

# ══════════════════════════════════════════════════
# STAGE 1 — THE FOUNDATION
# Goal: Working chatbot. v0.1.0 on GitHub.
# Timeline: This week
# Services: 6 (api, web, postgres, redis, qdrant, minio)
# ══════════════════════════════════════════════════

## GROUP 1 — Fix the Three Bugs (Do These First)

- [ ] **T-001: Fix missing env vars in docker-compose.yml**
  The co-op-api container needs several environment variables to start.
  Right now DB_PASS, DATABASE_URL, REDIS_URL, QDRANT_URL, MINIO_ENDPOINT,
  SECRET_KEY, ENVIRONMENT, and PYTHONPATH are missing from the co-op-api
  service section. Without them the API crashes immediately on startup.
  Open: `infrastructure/docker/docker-compose.yml`
  Add to co-op-api environment section:
    DATABASE_URL, DB_PASS, REDIS_URL, QDRANT_URL, MINIO_ENDPOINT,
    MINIO_ACCESS_KEY, MINIO_SECRET_KEY, SECRET_KEY, ENVIRONMENT, PYTHONPATH
  Also check: `infrastructure/docker/.env` has all values non-empty.
  **Done when:** `docker compose up` → api container starts, no "Field required" in logs

- [ ] **T-002: Run the missing database migration**
  The conversations table was created without a tenant_id column,
  but the SQLAlchemy model requires it.
  Run: `cd services/api && alembic upgrade head`
  Verify: `docker exec -it co-op-postgres-1 psql -U coop -d coop -c "\d conversations"`
  **Done when:** tenant_id column appears in the conversations table schema

- [ ] **T-003: Add python-multipart and rebuild the image**
  FastAPI uses python-multipart to parse form data. The login endpoint
  sends credentials as form-urlencoded, not JSON. Without this library,
  every login attempt returns a 500 error.
  Add to `services/api/pyproject.toml`: `"python-multipart>=0.0.9"`
  Rebuild: `docker compose build co-op-api && docker compose up -d co-op-api`
  **Done when:** `POST /v1/auth/token` with admin credentials returns a JSON object with access_token

## GROUP 2 — Verify Infrastructure Is Working

- [ ] **T-004: Confirm all 6 services start and pass health checks**
  Run: `docker compose -f infrastructure/docker/docker-compose.yml up -d`
  Run: `docker compose ps`
  **Done when:** all 6 rows show "Up (healthy)" in the Status column

- [ ] **T-005: Check the health endpoint returns all services ok**
  Run: `curl http://localhost:8000/health`
  **Done when:** response is `{"status":"ok","postgres":"ok","redis":"ok","qdrant":"ok"}`

- [ ] **T-006: Verify login returns a real JWT token**
  Run: `curl -X POST http://localhost:8000/v1/auth/token -d "username=admin@co-op.local&password=testpass123"`
  **Done when:** response contains "access_token" as a long JWT string

## GROUP 3 — Frontend Build Quality

- [ ] **T-007: Run the TypeScript build and fix every error**
  Run: `cd apps/web && pnpm build`
  Fix every error, one by one from top to bottom.
  **Done when:** `pnpm build` completes with exit code 0

- [ ] **T-008: Fix any hydration errors when refreshing pages**
  Test: open each page, press F5, watch the browser console
  **Done when:** zero red console errors on any page refresh

## GROUP 4 — End-to-End User Flow Testing

- [ ] **T-009: Test root URL redirects to login**
  Open: http://localhost:3000 in a browser (not logged in)
  **Done when:** browser redirects to http://localhost:3000/login

- [ ] **T-010: Test login and dashboard redirect**
  Enter admin@co-op.local and testpass123 in the login form.
  **Done when:** login succeeds and /dashboard loads without errors

- [ ] **T-011: Test dashboard health indicators are green**
  **Done when:** dashboard shows green status dots for all services

- [ ] **T-012: Test uploading a document and watching it reach READY**
  Upload a small PDF on the /documents page.
  **Done when:** uploaded document shows READY status with chunk_count > 0

- [ ] **T-013: Test searching the uploaded document**
  Go to /search and type a question related to the document content.
  **Done when:** search returns at least 1 result with content, score, and source

- [ ] **T-014: Test chat with streaming response and citations**
  Go to /chat and ask a question about the uploaded document.
  Note: this still uses stubbed inference — real LLM comes in Stage 2.
  **Done when:** chat shows a streaming response followed by a citation card

- [ ] **T-015: Test all sidebar navigation links**
  Click every item in the sidebar. Each page must load without a 404.
  **Done when:** every sidebar link loads its page

- [ ] **T-016: Check browser console shows zero red errors**
  Open DevTools Console, click through every page.
  **Done when:** zero red error messages on any page

## GROUP 5 — Repository and Release

- [ ] **T-017: Make sure .gitignore is correct**
  Confirm .env, .venv, node_modules, .next are all excluded.
  **Done when:** `git status` shows no sensitive files

- [ ] **T-018: Commit all working code**
  Run: `git add . && git commit -m "feat: Stage 1 complete — RAG pipeline + dark dashboard"`
  **Done when:** `git log` shows the commit

- [ ] **T-019: Push to GitHub and verify no secrets are visible**
  Run: `git push origin main`
  **Done when:** commit visible on GitHub with no .env files

- [ ] **T-020: Create the v0.1.0 release tag**
  Run: `git tag v0.1.0 -m "Stage 1: Company GPT working end-to-end"`
  Run: `git push origin v0.1.0`
  **Done when:** v0.1.0 tag visible on GitHub

### Stage 1 Summary: 20 tasks

---

# ══════════════════════════════════════════════════
# STAGE 2 — REAL INTELLIGENCE
# Goal: Real LLM + Telegram + Upwork search
# Timeline: Month 2 (4 weeks)
# New services: ollama, litellm (8 total)
# New code: arq workers, telegram bot, hardware detector,
#           lead scout agent
# ══════════════════════════════════════════════════

## WEEK 1 — Local LLM Setup

- [ ] **T-021: Add Ollama service to docker-compose.yml**
  Ollama serves local LLM models with an OpenAI-compatible API.
  Add to docker-compose.yml:
  ```yaml
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["ollama_data:/root/.ollama"]
  ```
  **Done when:** `curl http://localhost:11434/api/tags` returns a response

- [ ] **T-022: Download Llama models**
  Run: `docker exec ollama ollama pull llama3.2:3b`
  Run: `docker exec ollama ollama pull llama3.1:8b`
  **Done when:** both models listed in `docker exec ollama ollama list`

- [ ] **T-023: Create litellm_config.yaml with task routing**
  Create: `infrastructure/docker/litellm_config.yaml`
  Configure: simple tasks → llama3.2:3b, standard+ → llama3.1:8b
  Include: budget_manager settings per agent_id
  **Done when:** `curl localhost:4000/health` returns `{"status":"healthy"}`

- [ ] **T-024: Add LiteLLM service to docker-compose.yml**
  ```yaml
  litellm:
    image: ghcr.io/berriai/litellm:latest
    ports: ["4000:4000"]
    volumes: ["./litellm_config.yaml:/app/config.yaml"]
    command: ["--config", "/app/config.yaml"]
  ```
  **Done when:** `curl localhost:4000/v1/models` shows ollama models listed

- [ ] **T-025: Replace stubbed inference with real LiteLLM calls**
  Update the `generate_answer` LangGraph node in
  `services/api/app/agent/nodes.py` to call LiteLLM.
  **Done when:** chat returns coherent LLM-generated answers using document context

- [ ] **T-026: Build Hardware Detector (runs at startup)**
  Use psutil + py-cpuinfo. Reads RAM, GPU, assigns SOLO/TEAM/AGENCY tier.
  Writes to PostgreSQL settings table. Shows in dashboard header.
  Create: `services/api/app/core/hardware_detector.py`
  **Done when:** `curl /api/settings/hardware` shows correct tier

- [ ] **T-027: Check for KVM and set sandbox tier**
  At startup, check if /dev/kvm exists. Write sandbox_tier to settings.
  Show warning in dashboard if KVM not available.
  **Done when:** dashboard shows sandbox tier with appropriate message

## WEEK 2 — Background Workers with ARQ

- [ ] **T-028: Add arq to pyproject.toml**
  Add: `"arq>=0.25.0"` to `services/api/pyproject.toml`
  **Done when:** `pip install arq` completes without errors in the container

- [ ] **T-029: Create the ARQ worker settings and cron schedule**
  Create: `services/api/app/worker.py` with WorkerSettings class.
  **Done when:** `python -m arq app.worker.WorkerSettings` starts without errors

- [ ] **T-030: Run ARQ worker inside the co-op-api container**
  Use supervisord or entrypoint.sh to run both uvicorn and arq worker.
  **Done when:** `docker compose up` → both API and ARQ worker logs appear

- [ ] **T-031: Build System Monitor cron with Telegram alerts**
  Cron every 5 minutes: check Docker containers, API health, Redis queue.
  Self-heal on failure. Alert via Telegram if self-heal fails.
  **Done when:** stop a container → Telegram alert within 60 seconds

## WEEK 3 — Telegram Bot

- [ ] **T-032: Create a Telegram bot via BotFather**
  Get API token, store in `.env` as TELEGRAM_BOT_TOKEN.
  **Done when:** bot token saved in .env, bot appears in Telegram search

- [ ] **T-033: Add python-telegram-bot to pyproject.toml**
  Add: `"python-telegram-bot>=21.0"` to dependencies.
  **Done when:** library installs without errors

- [ ] **T-034: Build the Telegram adapter (inside co-op-api)**
  Create: `services/api/app/communication/telegram.py`
  Runs as an ARQ background task. Long-polling, no webhook needed.
  **Done when:** `/start` command returns "Co-Op is running. Send /help."

- [ ] **T-035: Implement all Telegram commands**
  Commands: /status, /pause, /resume, /panic, /approve, /budget, /help
  **Done when:** each command triggers correct system action

- [ ] **T-036: Build thinking display (numbered steps in Telegram)**
  Agents call send_progress() → same Telegram message updated with steps.
  Create: `services/api/app/communication/progress.py`
  **Done when:** running a test task shows live numbered updates in Telegram

- [ ] **T-037: Build credit tracker widget in dashboard**
  Read token usage from LiteLLM callback logs in PostgreSQL.
  Show live bar: green (normal), amber (80%), red (95%+).
  **Done when:** dashboard shows real-time token usage

## WEEK 4 — First Real Agent

- [ ] **T-038: Build Company Profile wizard**
  8-question browser conversation. Store in PostgreSQL as company_profiles.
  Index key facts in Qdrant (or pgvector).
  Create: `services/api/app/routers/company_setup.py`
  Update: `apps/web/src/app/(app)/company/page.tsx`
  **Done when:** completing wizard → profile visible in dashboard

- [ ] **T-039: Build Lead Scout agent (reads Upwork)**
  Uses httpx (not Browserless yet). Scores jobs 0-10. Reports top 5
  to Telegram with thinking display. READ-ONLY — no submissions.
  Create: `services/api/app/agent/lead_scout.py`
  Add to worker.py: cron every 4 hours.
  **Done when:** Lead Scout sends Telegram message with real job findings

- [ ] **T-040: Build Morning Brief cron**
  8am daily ARQ cron. Telegram: overnight activity, leads, health, budget.
  **Done when:** 8am Telegram message received with accurate data

- [ ] **T-041: Set up daily automated backup**
  Shell script: pg_dump, qdrant snapshot, minio sync. Run 2am via ARQ cron.
  **Done when:** backup runs, test restore works from backup files

- [ ] **T-042: Tag v0.2.0**
  Run: `git add . && git commit -m "feat: Stage 2 — Real LLM + Telegram + Lead Scout"`
  Run: `git tag v0.2.0 && git push origin main && git push origin v0.2.0`
  **Done when:** tag visible on GitHub

### Stage 2 Summary: 22 tasks

---

# ══════════════════════════════════════════════════
# STAGE 3 — WORKING AGENTS
# Goal: Proposals submitted. Clients talking. First revenue.
# Timeline: Months 3-4 (8 weeks)
# New services: browserless, vault, llm-guard, communication (12 total)
# ══════════════════════════════════════════════════

## MONTH 3, WEEK 1 — Browser and Security

- [ ] **T-043: Add Browserless to docker-compose.yml**
  ```yaml
  browserless:
    image: browserless/chrome:latest
    ports: ["8030:3000"]
    environment:
      - MAX_CONCURRENT_SESSIONS=2
      - CONNECTION_TIMEOUT=60000
      - ALLOWED_DOMAINS=upwork.com,linkedin.com,fiverr.com,github.com
  ```
  **Done when:** Playwright connects to `ws://localhost:8030` and fetches a page

- [ ] **T-044: Update Lead Scout to use Browserless**
  Replace httpx-based Upwork search with Playwright → Browserless.
  **Done when:** Lead Scout fetches real Upwork results via Browserless

- [ ] **T-045: Deploy HashiCorp Vault and migrate credentials**
  Add vault to docker-compose. Migrate all secrets from .env to Vault.
  Update services to fetch from Vault at startup using hvac library.
  **Done when:** .env contains no sensitive values, all from Vault

- [ ] **T-046: Deploy LLM Guard service**
  Add llm-guard to docker-compose. Wrap /v1/chat and /v1/search.
  Log all blocked requests to audit_events.
  **Done when:** send "ignore all previous instructions" → API returns 400

## MONTH 3, WEEK 2 — Communication Service

- [ ] **T-047: Build dedicated Communication service**
  Move Telegram bot from co-op-api into its own FastAPI service.
  Add Email adapter (SMTP + Gmail API).
  Create: `services/communication/` directory with own Dockerfile.
  Add to docker-compose on port 8010.
  **Done when:** Telegram commands still work, emails send via new service

- [ ] **T-048: Build thinking display in Communication service**
  POST /progress endpoint. Agents send updates here, service routes to Telegram.
  **Done when:** agent sends progress updates to Telegram via communication service

## MONTH 3, WEEK 3 — Proposal Writer Agent

- [ ] **T-049: Connect Composio MCP for Upwork API access**
  Register at composio.dev, store OAuth tokens in Vault.
  Add: `composio-core` to pyproject.toml.
  **Done when:** `upwork.search_jobs` tool call returns real job listings

- [ ] **T-050: Build Proposal Writer agent**
  RAG on portfolio docs in Qdrant. Drafts under 200 words.
  Self-reviews (specific? references job? under word limit?).
  Sends to HITL queue.
  Create: `services/api/app/agent/proposal_writer.py`
  **Done when:** real Upwork job → personalized proposal → HITL queue

- [ ] **T-051: Build HITL approval system**
  Risk levels: READ-ONLY (auto), LOW (auto+notify), MEDIUM (24h then reject),
  HIGH (24h then reject), CRITICAL (wait forever).
  Create: `services/api/app/routers/approvals.py` (full implementation)
  **Done when:** proposal in queue → `/approve 1` → Telegram confirms

- [ ] **T-052: Build auto-approval rule engine**
  YAML config: which action types auto-approve after N successes.
  Never auto-approve: proposals, invoices, payments.
  Create: `.coop/auto-approval.yaml`
  **Done when:** follow-up email #4 auto-approves, proposal #1 requires human

## MONTH 3, WEEK 4 — Outreach and First Submission

- [ ] **T-053: Build Outreach Manager agent**
  Submit approved proposals via Composio. 3-day follow-up reminder.
  Create: `services/api/app/agent/outreach_manager.py`
  **Done when:** approved proposal → submitted to real Upwork → Telegram confirmation

- [ ] **T-054: Set up prompt versioning in PostgreSQL**
  Store every agent prompt in DB table with version and performance metrics.
  Create: `prompt_versions` table.
  **Done when:** Proposal Writer loads its prompt from DB at runtime

- [ ] **T-055: Tag v0.3.0**
  **Done when:** tag visible on GitHub

## MONTH 4, WEEK 1 — Client Communication

- [ ] **T-056: Build Client Communicator agent**
  Handles incoming client messages via email. Professional tone.
  Never claims to be human if asked. Escalates complex items to HITL.
  Create: `services/api/app/agent/client_communicator.py`
  **Done when:** client email received → agent drafts response → HITL queue

- [ ] **T-057: Build Project Tracker agent**
  Creates milestones from project requirements. 72h deadline alerts.
  Weekly status update drafts (human approves before sending).
  Create: `services/api/app/agent/project_tracker.py`
  **Done when:** project created → milestones set → 72h warning in Telegram

- [ ] **T-058: Build Finance Manager agent**
  Creates invoices from milestones. Human approves before sending.
  7-day payment reminder workflow using ARQ.
  Create: `services/api/app/agent/finance_manager.py`
  **Done when:** milestone complete → invoice created → in approval queue

## MONTH 4, WEEK 2 — Polish and Tools

- [ ] **T-059: Build Simulation Mode (dashboard toggle)**
  [Live] ↔ [Simulation] toggle. Fake Upwork jobs, fake client personas.
  All sends intercepted. Metrics tracked identically.
  **Done when:** toggle to Simulation → fake jobs appear → no real submissions

- [ ] **T-060: Add pgvector-based semantic search (optional)**
  Only do this if Qdrant is consuming too much RAM on your machine.
  Run: `CREATE EXTENSION vector` in PostgreSQL.
  Replace Qdrant client calls with pgvector queries.
  **Done when:** semantic search works through PostgreSQL without Qdrant
  **(optional — skip unless RAM is a problem)**

- [ ] **T-061: Build client portal page**
  Simple read-only page for clients. HMAC-signed URL, no login.
  Shows project name, milestone, completion %, recent updates.
  Create: `apps/web/src/app/portal/[token]/page.tsx`
  **Done when:** client receives URL and sees project status page

- [ ] **T-062: Set up prompt quality CI with GitHub Actions**
  GitHub Actions: runs DeepEval on any PR touching prompts.
  Create: `.github/workflows/prompt-quality.yml`
  **Done when:** PR with prompt change → CI posts evaluation results

## MONTH 4, WEEK 3 — Research and Improvement

- [ ] **T-063: Build Research Agent v1**
  Scans GitHub Trending and HuggingFace weekly. Scores relevance 0-10.
  If > 7/10: runs micro-benchmark in Docker sandbox.
  Create: `services/api/app/agent/research_agent.py`
  Add: cron weekly (Sunday 9pm) in worker.py.
  **Done when:** weekly Telegram message with real discovery and benchmark

- [ ] **T-064: Build Docker sandbox for code execution**
  Simple secure code runner using Docker. Network disabled, memory limited.
  Create: `services/api/app/core/docker_sandbox.py`
  Note: Replace with microsandbox (microVM) in Stage 4 when needed.
  **Done when:** code executes inside Docker with no host network access

- [ ] **T-065: Full end-to-end revenue test**
  Walk through the complete flow: Lead finds job → proposal approved →
  submitted → client replies → agent responds → project tracked →
  invoice created → payment received.
  **Done when:** this full flow has been completed at least once with a real client

- [ ] **T-066: Tag v0.4.0 — First Revenue Version**
  **Done when:** tag visible on GitHub

## MONTH 4, WEEK 4 — Code Delivery Capability (Optional)

- [ ] **T-067: Add code-server to docker-compose.yml (optional)**
  code-server = VS Code in browser. Developer Agent writes code via API.
  ```yaml
  code-server:
    image: linuxserver/code-server:latest
    ports: ["8443:8443"]
    volumes: ["code_workspace:/config/workspace"]
  ```
  Only add if you want to deliver websites/apps to clients.
  **Done when:** VS Code accessible at http://localhost:8443
  **(optional — skip unless delivering code projects)**

- [ ] **T-068: Build Developer Agent (optional)**
  Writes code using code-server, tests in Docker sandbox.
  Quality Reviewer checks result. You do final review.
  Create: `services/api/app/agent/developer_agent.py`
  **Done when:** developer agent creates GitHub repo, writes code, tests pass
  **(optional — skip unless delivering code projects)**

### Stage 3 Summary: 26 tasks (2 optional)

---

# ══════════════════════════════════════════════════
# STAGE 4 — ADD FULL V5.3 COMPONENTS
# Add only when you feel the specific pain
# Month 5 onward
# ══════════════════════════════════════════════════

## SCALE UP TRIGGERS AND TASKS

Each task below starts with its TRIGGER — the pain that tells you it is time.
Do not add any of these preemptively.

### TRIGGER: "ARQ loses tasks when container restarts mid-workflow"

- [ ] **T-069: Deploy Temporal workflow engine**
  Temporal stores workflow state in its own PostgreSQL database.
  Even if your container crashes mid-execution, the workflow resumes.
  Add: temporal (port 7233) + temporal-ui (port 8088) to docker-compose.
  Migrate: proposal pipeline from ARQ to Temporal workflow.
  **Done when:** Temporal UI shows workflow history, crash recovery works

- [ ] **T-070: Add zombie agent detector**
  Checks if any Temporal workflow runs > 2x its average duration.
  If yes: pauses LiteLLM calls, snapshots state, alerts Telegram.
  Requires: Temporal running first.
  **Done when:** simulated stuck workflow → detected and paused in 10 minutes

### TRIGGER: "Upwork/scraping keeps getting blocked"

- [ ] **T-071: Upgrade Browserless with proxy rotation**
  Configure residential proxies to appear as different users/locations.
  **Done when:** Lead Scout runs without blocks for 7 consecutive days

- [ ] **T-072: Add scraper abstraction layer**
  Separate executor files per platform (upwork_v1.py, upwork_v2.py).
  **Done when:** switching scraper version requires changing 1 file only

### TRIGGER: "I need proper debugging — why did the agent do that?"

- [ ] **T-073: Deploy OpenTelemetry + Grafana Tempo**
  Distributed tracing across all services.
  Add: otel-collector, grafana-tempo, prometheus, grafana to docker-compose.
  **Done when:** Grafana at localhost:3001 shows agent execution traces

### TRIGGER: "Docker sandbox feels unsafe for client code"

- [ ] **T-074: Replace Docker sandbox with microsandbox (microVM)**
  Requires: KVM enabled on your machine (/dev/kvm must exist).
  **Done when:** code runs in microsandbox, `coop doctor` shows TIER 1

### TRIGGER: "Code tasks take 2+ minutes because npm/pip is slow"

- [ ] **T-075: Deploy Verdaccio + devpi (local package caches)**
  Add: verdaccio (port 4873), devpi (port 3141) to docker-compose.
  **Done when:** `npm install` in sandbox fetches from localhost

### TRIGGER: "15+ agents and LLM is a bottleneck at peak hours"

- [ ] **T-076: Deploy vLLM (if you have a GPU)**
  Add: vllm service on port 8001.
  Update: litellm_config.yaml to route standard+ tasks to vLLM.
  **Done when:** GPU utilization visible, response time improves

- [ ] **T-077: Alternatively: upgrade to Groq paid API**
  Add Groq API key to Vault. LiteLLM routes overflow to Groq.
  **Done when:** overflow tasks route to Groq when Ollama is busy

### TRIGGER: "Complex permission rules for a team of 3+"

- [ ] **T-078: Deploy Open Policy Agent (OPA)**
  Centralized policy engine with Rego rules.
  Add: opa service on port 8181.
  **Done when:** policy files control tool access, violations are blocked

### TRIGGER: "Messages getting lost between services at high load"

- [ ] **T-079: Deploy NATS JetStream**
  Distributed, persistent message queuing.
  Add: nats service on port 4222.
  **Done when:** NATS handles all inter-service events

### TRIGGER: "50+ clients and need relationship intelligence"

- [ ] **T-080: Deploy Neo4j for Graphiti memory**
  Graph database for client relationship queries.
  Add: neo4j service on port 7474.
  **Done when:** Graphiti stores client graph, query time < 100ms

### TRIGGER: "Revenue > £10k/month, need to scale"

- [ ] **T-081: Add Traefik API gateway**
  TLS, rate limiting, request routing.
  **Done when:** API accessible via HTTPS, rate limiting active

- [ ] **T-082: Add enterprise SSO (Keycloak)**
  OIDC/SAML for Google Workspace, Okta, Azure AD.
  **Done when:** login via Google Workspace SSO works

- [ ] **T-083: Set up Helm charts for Kubernetes**
  Full stack as Helm charts.
  **Done when:** `helm install co-op` deploys full stack

### Stage 4 Summary: 15 tasks (add only when triggered)

---

# TASK COUNT SUMMARY

| Stage | Tasks | When | Goal |
|-------|-------|------|------|
| Stage 1 | 20 tasks | This week | Working chatbot, v0.1.0 on GitHub |
| Stage 2 | 22 tasks | Month 2 | Real LLM, Telegram, Upwork reading |
| Stage 3 | 26 tasks (2 optional) | Month 3-4 | Proposals submitted, first revenue |
| Stage 4 | 15 tasks (triggered) | Month 5+ | Add only when you feel the pain |

**Stage 1-3 total: 68 tasks over 4 months.**
All achievable solo with AI IDE assistance.

---

# HOW TO USE YOUR AI IDE FOR EACH TASK

Before giving a task to your AI IDE, always:

1. **Tell it which stage and task you are on**
   "I am working on Stage 2, T-034, Telegram adapter task"

2. **Share the relevant existing files as context**
   - `services/api/app/main.py`
   - `services/api/app/config.py`
   - `infrastructure/docker/docker-compose.yml`
   - This task description

3. **Give it the exact "Done when" criteria**
   "The task is complete when: /start command returns system status"

4. **Set boundaries for the current stage**
   "We are in Stage 2. Do not add Temporal, NATS, OPA, or Neo4j.
    Use ARQ instead of Celery. Use PostgreSQL JSONB instead of Neo4j."

5. **Verify the "Done when" before marking complete**
   Do not trust that code looks correct — run the actual test.

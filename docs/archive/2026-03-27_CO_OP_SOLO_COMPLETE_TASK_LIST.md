# Co-Op Solo Developer — Complete Task List
# Step-by-step with explanations for every task
# 4 Stages | ~4 months to first revenue

---

## HOW TO USE THIS LIST
- Work top to bottom, never skip ahead
- Each task has: what to do + why it matters + done when
- The "Done when" step is mandatory — check it before moving on
- Mark [x] when complete
- If a task blocks you for more than 2 hours, ask your AI IDE for help

---

# ══════════════════════════════════════════════════
# STAGE 1 — THE FOUNDATION
# Goal: Working chatbot. v0.1.0 on GitHub.
# Timeline: This week
# Services: 6 (api, web, postgres, redis, qdrant, minio)
# ══════════════════════════════════════════════════

## GROUP 1 — Fix the Three Bugs (Do These First)

- [ ] **Fix missing env vars in docker-compose.yml**
  The co-op-api container needs several environment variables to start.
  Right now DB_PASS, DATABASE_URL, REDIS_URL, QDRANT_URL, MINIO_ENDPOINT,
  SECRET_KEY, ENVIRONMENT, and PYTHONPATH are missing from the co-op-api
  service section. Without them the API crashes immediately on startup
  before handling a single request.
  Open: infrastructure/docker/docker-compose.yml
  Add to co-op-api environment section:
    DATABASE_URL: "postgresql+asyncpg://coop:${DB_PASS}@postgres:5432/coop"
    DB_PASS: "${DB_PASS}"
    REDIS_URL: "redis://redis:6379"
    QDRANT_URL: "http://qdrant:6333"
    MINIO_ENDPOINT: "minio:9000"
    MINIO_ACCESS_KEY: "${MINIO_ACCESS_KEY}"
    MINIO_SECRET_KEY: "${MINIO_SECRET_KEY}"
    SECRET_KEY: "${SECRET_KEY}"
    ENVIRONMENT: "development"
    PYTHONPATH: "/app"
  Also check: infrastructure/docker/.env has all these values non-empty.
  Done when: docker compose up → api container starts, no "Field required" in logs

- [ ] **Run the missing database migration**
  The conversations table was created without a tenant_id column, but
  the SQLAlchemy model requires it. Every request to the chat endpoint
  fails with "column conversations.tenant_id does not exist". This is an
  Alembic migration that already exists in the repo but was never applied.
  Run: cd services/api && alembic upgrade head
  Verify: docker exec -it co-op-postgres-1 psql -U coop -d coop -c "\d conversations"
  Done when: tenant_id column appears in the conversations table schema

- [ ] **Add python-multipart and rebuild the image**
  FastAPI uses python-multipart to parse form data. The login endpoint
  sends credentials as form-urlencoded, not JSON. Without this library,
  every login attempt returns a 500 error even with correct credentials.
  Open: services/api/pyproject.toml
  Add: "python-multipart>=0.0.9" to the dependencies list
  Rebuild: docker compose build co-op-api && docker compose up -d co-op-api
  Done when: curl -X POST http://localhost:8000/v1/auth/token
             -d "username=admin@co-op.local&password=testpass123"
             returns a JSON object with an access_token field

## GROUP 2 — Verify Infrastructure Is Working

- [ ] **Confirm all 6 services start and pass health checks**
  After fixing the bugs, all 6 services need to be running and healthy
  before you can test anything. Docker health checks confirm that services
  are not just started but actually ready to handle requests.
  Run: docker compose -f infrastructure/docker/docker-compose.yml up -d
  Run: docker compose ps
  Done when: all 6 rows show "Up (healthy)" in the Status column

- [ ] **Check the health endpoint returns all services ok**
  The /health endpoint makes live connections to PostgreSQL, Redis, and
  Qdrant to confirm they are reachable from inside the API container.
  A healthy container does not always mean the connections inside work.
  Run: curl http://localhost:8000/health
  Done when: response is {"status":"ok","postgres":"ok","redis":"ok","qdrant":"ok"}

- [ ] **Verify login returns a real JWT token**
  Test the complete authentication flow from outside the container.
  This confirms the auth endpoint, database connection, and password
  verification are all working together.
  Run: curl -X POST http://localhost:8000/v1/auth/token
       -H "Content-Type: application/x-www-form-urlencoded"
       -d "username=admin@co-op.local&password=testpass123"
  Done when: response contains "access_token" as a long JWT string

## GROUP 3 — Frontend Build Quality

- [ ] **Run the TypeScript build and fix every error**
  The frontend must compile cleanly before it can be considered working.
  TypeScript errors often indicate real bugs, not just style issues.
  Running the build finds every problem before a user does.
  Run: cd apps/web && pnpm build
  Fix every error shown in the output, one by one from top to bottom.
  Common issues: missing imports, wrong prop types, undefined variables.
  Done when: pnpm build completes with exit code 0 and "Compiled successfully"

- [ ] **Fix any hydration errors when refreshing pages**
  Next.js renders pages on the server first, then on the client. If the
  HTML they produce is different, React throws a hydration error. These
  show up as red errors in the browser console and cause parts of the
  page to break or flash.
  Test: open each page, press F5, watch the browser console
  Done when: zero red console errors on any page refresh

## GROUP 4 — End-to-End User Flow Testing

- [ ] **Test that the root URL redirects to login**
  When a user visits http://localhost:3000 without being logged in,
  they should be redirected to /login automatically. This is the entry
  point for all users and must work correctly.
  Open: http://localhost:3000 in a browser (not logged in)
  Done when: browser redirects to http://localhost:3000/login

- [ ] **Test login and dashboard redirect**
  Enter admin@co-op.local and testpass123 in the login form.
  After successful login the app should store the JWT token and
  redirect to the dashboard. The token is stored in localStorage
  and used for all subsequent API calls.
  Done when: login succeeds and /dashboard loads without errors

- [ ] **Test dashboard health indicators are green**
  The dashboard calls the /health endpoint every 30 seconds and shows
  colored dots for each service. All dots should be green if the
  infrastructure is healthy. This is the first live data on the dashboard.
  Done when: dashboard shows green status indicators for all services

- [ ] **Test uploading a document and watching it reach READY**
  Upload a small PDF on the /documents page. Watch the status badge
  change from PENDING to INDEXING to READY. This tests the entire
  document processing pipeline: file upload, MinIO storage, Redis event,
  background worker, text parsing, embedding generation, and Qdrant indexing.
  Done when: uploaded document shows READY status with chunk_count greater than 0

- [ ] **Test searching the uploaded document**
  Go to /search and type a question related to the document content.
  Results should appear within 2 seconds with source filename, page number,
  and a relevance score. This confirms the RAG retrieval pipeline works.
  Done when: search returns at least 1 result with content, score, and source

- [ ] **Test chat with streaming response and citations**
  Go to /chat and ask a question about the uploaded document. The response
  should stream word by word and include a citation card showing which
  document and page the answer came from. Note: this still uses stubbed
  inference at Stage 1 — the answer comes from RAG chunks, not a real LLM.
  Done when: chat shows a streaming response followed by a citation card

- [ ] **Test all 10 navigation links in the sidebar**
  Click every item in the sidebar: dashboard, chat, documents, search,
  agents, approvals, admin, and any others. Each page must load without
  a 404 error or blank screen. Some pages will show empty state which
  is correct.
  Done when: clicking every sidebar link loads its page without errors

- [ ] **Check browser console shows zero red errors**
  Open Chrome/Firefox DevTools (F12), go to the Console tab, and click
  through every page. Red errors indicate broken functionality.
  Yellow warnings are usually acceptable.
  Done when: zero red error messages on any page

## GROUP 5 — Repository and Release

- [ ] **Make sure .gitignore is correct**
  The .gitignore file must prevent sensitive files from being committed.
  The most important exclusions are .env files (contain passwords and keys),
  .venv (Python virtual environments), node_modules, and .next.
  Check: cat .gitignore and confirm these patterns exist
  Run: git status — confirm no .env or .venv files appear as untracked
  Done when: git status shows no sensitive files staged or untracked

- [ ] **Commit all working code**
  Stage all files and write a descriptive commit message. Future
  contributors will read this to understand what Phase 0 delivers.
  Run: git add .
  Run: git commit -m "feat: Stage 1 complete — RAG pipeline + dark dashboard"
  Done when: git log shows the commit with the correct message

- [ ] **Push to GitHub and verify no secrets are visible**
  Push the commit to the remote repository. Then open GitHub in a browser
  and check that no .env files appear in the file browser. If they do,
  remove them from the repo immediately (they contain passwords).
  Run: git push origin main
  Done when: commit visible at github.com/NAVANEETHVVINOD/CO_OP with no .env files

- [ ] **Create the v0.1.0 release tag**
  Git tags permanently mark specific points in history. The v0.1.0 tag
  means Stage 1 is complete and verified. Anyone can checkout this tag
  to get exactly the Stage 1 state of the project.
  Run: git tag v0.1.0 -m "Stage 1: Company GPT working end-to-end"
       git push origin v0.1.0
  Done when: v0.1.0 tag visible in GitHub under Tags or Releases

---

# ══════════════════════════════════════════════════
# STAGE 2 — REAL INTELLIGENCE
# Goal: Real LLM + Telegram + Upwork search
# Timeline: Month 2 (4 weeks)
# New services: ollama (8 total)
# New code: litellm config, arq workers, telegram bot,
#           hardware detector, lead scout agent
# ══════════════════════════════════════════════════

## WEEK 1 — Local LLM Setup

- [ ] **Add Ollama service to docker-compose.yml**
  Ollama serves local LLM models (Llama, Mistral, etc.) directly on your
  machine. It is an OpenAI-compatible API so LiteLLM can route to it
  without any special code. You need a volume mount so downloaded models
  survive container restarts (they are several GB each).
  Add to docker-compose.yml:
    ollama:
      image: ollama/ollama:latest
      ports: ["11434:11434"]
      volumes: ["ollama_data:/root/.ollama"]
  Done when: curl http://localhost:11434/api/tags returns a response

- [ ] **Download Llama models**
  Ollama needs to download the actual model files before it can answer
  questions. Llama 3.2 3B is the fast model for simple tasks. Llama 3.1
  8B is the quality model for proposals and analysis. Each takes a few
  minutes to download (3-5GB each).
  Run: docker exec ollama ollama pull llama3.2:3b
  Run: docker exec ollama ollama pull llama3.1:8b
  Done when: both models listed in docker exec ollama ollama list

- [ ] **Create litellm_config.yaml with task routing**
  LiteLLM is the gateway that sits between your code and any LLM. You
  configure it once in a YAML file. The task router sends simple tasks
  (formatting, classification) to the fast 3B model and complex tasks
  (writing proposals, analysis) to the 8B model. This saves tokens
  and is faster for routine operations.
  Create: infrastructure/docker/litellm_config.yaml
  Content should define:
    - model: ollama/llama3.2:3b for simple tasks
    - model: ollama/llama3.1:8b for standard tasks
    - budget_manager settings per agent_id
  Done when: curl localhost:4000/health returns {"status":"healthy"}

- [ ] **Add LiteLLM service to docker-compose.yml**
  LiteLLM runs as a separate service that wraps Ollama. All your Python
  code calls LiteLLM, not Ollama directly. This means you can swap models
  later without changing any agent code. The budget enforcement also
  lives here — LiteLLM blocks calls when an agent exceeds its daily limit.
  Add to docker-compose.yml:
    litellm:
      image: ghcr.io/berriai/litellm:latest
      ports: ["4000:4000"]
      volumes: ["./litellm_config.yaml:/app/config.yaml"]
      command: ["--config", "/app/config.yaml"]
  Done when: curl localhost:4000/v1/models shows ollama models listed

- [ ] **Replace stubbed inference with real LiteLLM calls**
  The chat endpoint currently returns placeholder text assembled from
  RAG chunks. Update the generate_answer LangGraph node to call
  LiteLLM with the RAG context. Now answers will be genuinely reasoned
  responses grounded in your documents.
  File: services/api/app/agent/nodes.py — update generate_answer function
  Test: upload a PDF, ask a question, verify the answer reads naturally
  Done when: chat returns a coherent LLM-generated answer citing document content

- [ ] **Build Hardware Detector (runs at startup)**
  The hardware detector reads your machine's CPU cores, RAM amount, and
  whether a GPU is present. It writes a recommended configuration to the
  PostgreSQL settings table. The dashboard header will show your tier
  (SOLO/TEAM/AGENCY) and the coop doctor command uses this for advice.
  Use: psutil and py-cpuinfo Python libraries
  Create: services/api/app/core/hardware_detector.py
  Call it: in services/api/app/main.py lifespan startup event
  Done when: coop doctor (or curl /api/settings/hardware) shows correct tier

- [ ] **Check for KVM and set sandbox tier**
  microVM sandboxes (microsandbox) require KVM virtualization support.
  Not all machines and VPS providers have it enabled. At startup, check
  if /dev/kvm exists. Write the sandbox tier to PostgreSQL settings.
  Show a clear warning in the dashboard if you are on Tier 3 (Docker only).
  Add to hardware_detector.py: check /dev/kvm, write sandbox_tier to settings
  Done when: dashboard shows sandbox tier and warning if KVM not available

## WEEK 2 — Background Workers with ARQ

- [ ] **Add arq to pyproject.toml**
  ARQ (Async Redis Queue) is a simple background task library that works
  natively with asyncio and FastAPI. It uses Redis as its broker (which
  you already have running). Unlike Celery, it requires no separate config
  files and runs inside your existing container as a second process.
  Add to services/api/pyproject.toml dependencies: "arq>=0.25.0"
  Done when: pip install arq completes without errors in the container

- [ ] **Create the ARQ worker settings and cron schedule**
  Create a WorkerSettings class that lists all your background functions
  and their cron schedules. The worker reads from Redis and executes tasks
  when they come in or when their cron time arrives.
  Create: services/api/app/worker.py
  Include: WorkerSettings class with empty functions list for now
  Done when: python -m arq app.worker.WorkerSettings starts without errors

- [ ] **Run ARQ worker inside the co-op-api container**
  ARQ worker runs as a second process alongside the FastAPI server. Use
  supervisord or a simple shell script to start both processes when the
  container starts. This avoids needing a separate container at this stage.
  Update: services/api/Dockerfile to use supervisord or entrypoint.sh
  Update: supervisord.conf or entrypoint.sh to start both uvicorn and arq
  Done when: docker compose up → both API and ARQ worker logs appear

- [ ] **Build System Monitor cron with Telegram alerts**
  A background function that runs every 5 minutes. It checks that all
  6 Docker services are healthy, that the Redis queue is not backed up,
  and that the LiteLLM API is responding. If anything is wrong, it tries
  to fix it (docker restart) and sends a Telegram alert if that fails.
  This is your 24/7 watchdog — it runs even while you sleep.
  Add to worker.py: system_monitor_task function + cron every 5 minutes
  Done when: stop one service → system monitor alert received in Telegram within 5 min

## WEEK 3 — Telegram Bot

- [ ] **Create a Telegram bot via BotFather**
  Go to @BotFather on Telegram, send /newbot, choose a name and username.
  BotFather gives you an API token. Store this in infrastructure/docker/.env
  as TELEGRAM_BOT_TOKEN. This is the credential your bot uses to send and
  receive messages.
  Done when: bot token saved in .env, bot appears in Telegram search

- [ ] **Add python-telegram-bot to pyproject.toml**
  python-telegram-bot is the official Telegram Bot API library for Python.
  It handles message receiving, command parsing, and message sending.
  Add: "python-telegram-bot>=21.0" to dependencies
  Done when: library installs without errors in the container

- [ ] **Build the Telegram adapter (inside co-op-api, no new container)**
  Create a Telegram adapter that starts as an ARQ background task.
  It uses long-polling (no webhook needed) to receive messages from
  Telegram and dispatches commands to the right handlers.
  Create: services/api/app/communication/telegram.py
  Add to worker.py: start_telegram_bot function that runs at startup
  Done when: /start command to your bot returns "Co-Op is running. Send /help."

- [ ] **Implement all Telegram commands**
  These are the commands your bot understands. Each one either queries
  the API or triggers an action. This is your primary control interface
  when you are away from the dashboard.
  Implement these handlers in telegram.py:
  /status   — shows all running agents and system health
  /pause    — suspends all ARQ tasks
  /resume   — resumes suspended tasks
  /panic    — immediately stops all agents and queued tasks
  /approve  — approves HITL items (e.g. /approve 1 3)
  /budget   — shows current token usage vs daily limits
  /help     — lists all commands with descriptions
  Done when: each command returns the expected response

- [ ] **Build thinking display (numbered steps sent to Telegram)**
  As agents work, they should send progress updates to Telegram so you
  know what is happening without opening the dashboard. Implement a
  progress publisher: agents call a send_progress() function that updates
  the same Telegram message with numbered steps.
  Create: services/api/app/communication/progress.py
  Use: telegram.Bot.edit_message_text to update the same message with new steps
  Done when: running a test task shows live numbered updates in Telegram

- [ ] **Build credit tracker widget in the dashboard**
  Add a live token usage widget to the dashboard top bar. It reads
  LiteLLM's callback logs from PostgreSQL and shows a progress bar per
  agent: green (normal), amber (80% of daily budget), red (95%+).
  Alert at 80% via Telegram too.
  Add: LiteLLM callback that writes token usage to cost_events table
  Update: dashboard top bar to query and display usage
  Done when: dashboard shows real-time token bar updating as chat is used

## WEEK 4 — First Real Agent

- [ ] **Build the Company Profile wizard**
  A browser-based conversation flow (8 questions) that asks about your
  business in plain English: what type of company, what services, what
  rates, target clients, geography, communication style. Stores the
  answers as a structured JSON profile in PostgreSQL and indexes the
  content in Qdrant so agents can retrieve it when writing proposals.
  Create: services/api/app/routers/company_setup.py (wizard API)
  Update: apps/web/src/app/(app)/company/page.tsx (wizard UI)
  Done when: completing the wizard shows company profile in dashboard

- [ ] **Build Lead Scout agent (reads Upwork, no submitting)**
  The Lead Scout searches Upwork for jobs matching your company profile.
  At this stage it uses httpx (a Python HTTP library) to call the Upwork
  API or search page. It scores each job 0-10 based on match with your
  profile and skills. Reports the top 5 to Telegram with thinking display.
  It does NOT submit any proposals yet — human review only.
  Create: services/api/app/agent/lead_scout.py
  Add to worker.py: lead_scout_task cron every 4 hours
  Done when: Lead Scout sends a real Telegram message with Upwork job findings

- [ ] **Add arq cron for the morning brief**
  A cron that runs every morning at 8am and sends a Telegram message
  summarizing overnight activity: new leads found, active project status,
  system health, token usage vs budget, and any alerts from overnight.
  This is your daily operating summary.
  Add to worker.py: morning_brief_task cron at hour=8, minute=0
  Done when: 8am Telegram message received with accurate data for your system

- [ ] **Set up daily automated backup**
  A cron that runs every night at 2am and backs up all your data.
  PostgreSQL dump, Qdrant collection snapshots, and MinIO files copied
  to a local backup directory. Without this, a drive failure means
  losing all your clients, proposals, and agent memory.
  Add to worker.py: backup_task cron at hour=2, minute=0
  The task runs pg_dump and calls Qdrant's snapshot API.
  Done when: backup runs at 2am, restore test from backup files passes

- [ ] **Tag v0.2.0**
  Stage 2 is complete. You have a real LLM responding, Telegram control
  working, and an agent actually reading Upwork jobs.
  Run: git add . && git commit -m "feat: Stage 2 — Real LLM + Telegram + Lead Scout"
       git tag v0.2.0 && git push origin main && git push origin v0.2.0
  Done when: tag visible on GitHub

---

# ══════════════════════════════════════════════════
# STAGE 3 — WORKING AGENTS
# Goal: Proposals submitted. Clients talking. First revenue.
# Timeline: Months 3-4 (8 weeks)
# New services: browserless, vault, llm-guard, communication
# ══════════════════════════════════════════════════

## MONTH 3, WEEK 1 — Browser and Security

- [ ] **Add Browserless to docker-compose.yml**
  Browserless runs a headless Chrome browser inside Docker. Agents
  connect to it using the standard Playwright API but via WebSocket
  instead of launching a local browser. Browserless handles anti-bot
  detection and session persistence. You need this because Upwork will
  block httpx requests after a few days — Browserless looks like a real browser.
  Add to docker-compose.yml:
    browserless:
      image: browserless/chrome:latest
      ports: ["8030:3000"]
      environment:
        - MAX_CONCURRENT_SESSIONS=2
        - CONNECTION_TIMEOUT=60000
        - ALLOWED_DOMAINS=upwork.com,linkedin.com,fiverr.com,github.com
  Done when: Playwright can connect to ws://localhost:8030 and fetch a page

- [ ] **Update Lead Scout to use Browserless**
  Replace the httpx-based Upwork search with Playwright connecting to
  Browserless. This makes Lead Scout look like a real browser, handles
  JavaScript-rendered pages, and manages login sessions properly.
  Update: services/api/app/agent/lead_scout.py to use playwright
  Configure: BROWSERLESS_URL setting in config.py
  Done when: Lead Scout fetches real Upwork search results via Browserless

- [ ] **Deploy HashiCorp Vault and migrate credentials**
  You are about to store Upwork credentials, email tokens, and API keys.
  These cannot stay in .env files. Vault stores secrets encrypted and
  gives each service a scoped token at runtime. Agents never see raw
  credentials — they request the action, Vault injects the credential.
  Add to docker-compose.yml: vault service
  Migrate: TELEGRAM_BOT_TOKEN, MINIO keys, SECRET_KEY to Vault
  Update: services to fetch from Vault on startup using hvac Python library
  Done when: .env contains no sensitive values, all fetched from Vault

- [ ] **Deploy LLM Guard service**
  LLM Guard scans all text going into and coming out of the LLM.
  It detects prompt injection attacks (someone trying to hijack your agent),
  anonymizes PII (phone numbers, email addresses) before they reach the LLM,
  and blocks toxic content. You need this now because agents will soon
  receive external content from job descriptions and client messages.
  Add to docker-compose.yml: llm-guard service
  Wrap: /v1/chat and /v1/search endpoints in main.py
  Done when: send "ignore all previous instructions" → API returns 400

## MONTH 3, WEEK 2 — Communication Service

- [ ] **Build dedicated Communication service**
  Move the Telegram bot out of co-op-api into its own FastAPI service.
  Add an Email adapter (SMTP for sending, IMAP for receiving). This
  service becomes the single place where all external communication
  flows through — easier to debug and add new platforms later.
  Create: services/communication/ directory with own Dockerfile
  Add to docker-compose.yml: communication service on port 8010
  Move: Telegram adapter from co-op-api to new service
  Done when: Telegram commands still work, emails send via new service

- [ ] **Build thinking display in Communication service**
  Agents should be able to send progress updates from any service.
  Create a simple REST endpoint in the communication service:
  POST /progress {agent_id, step_number, total_steps, message, status}
  The service routes this to the right platform (Telegram in this case).
  This replaces the progress publisher you built in Stage 2.
  Create: POST /progress endpoint in communication service
  Update: agent code to call this endpoint instead of Telegram directly
  Done when: agent running in agent-runtime sends updates to Telegram via communication service

## MONTH 3, WEEK 3 — Proposal Writer Agent

- [ ] **Connect Composio MCP for Upwork API access**
  Composio gives you a managed integration to Upwork's official API.
  This is cleaner than scraping and less likely to get you banned.
  Store your Upwork OAuth token in Vault. Composio handles token refresh.
  Register at composio.dev, get API key, store in Vault.
  Add: composio-core to pyproject.toml
  Configure: Upwork connection in Composio dashboard
  Done when: tool call to upwork.search_jobs returns real job listings

- [ ] **Build Proposal Writer agent using portfolio RAG**
  The Proposal Writer reads your portfolio documents from Qdrant and your
  company profile from PostgreSQL. It drafts a personalized proposal for
  each job under 200 words. It self-reviews before sending: Is it specific
  to this job? Does it reference my relevant experience? Is it under 200 words?
  Create: services/api/app/agent/proposal_writer.py
  The agent uses Qdrant to retrieve relevant portfolio examples for each job.
  Done when: real Upwork job → personalized proposal drafted → sent to approval queue

- [ ] **Build the HITL approval system**
  HITL (Human in the Loop) means agents pause and wait for your decision
  before taking certain actions. Every proposal must be reviewed by you
  before being submitted. The approval queue stores pending items in
  PostgreSQL. You review them in the dashboard or via Telegram.
  Create: services/api/app/routers/approvals.py (full implementation)
  Update: dashboard /approvals page to show evidence with each item
  Add Telegram: "3 proposals ready — /approve 1 2 3 or /reject all"
  Done when: proposal in queue → /approve 1 → Telegram confirms proposal approved

- [ ] **Build auto-approval rule engine**
  Not every action needs manual review. Sending a follow-up email to a
  client who has not replied in 3 days is low risk. You can configure
  certain action types to auto-approve after they have succeeded N times.
  Proposals and invoices should never auto-approve.
  Create: .coop/auto-approval.yaml config file
  Implement: rule engine checks in approvals router before queuing
  Done when: follow-up email #4 auto-approves, proposal #1 requires human review

## MONTH 3, WEEK 4 — Outreach and First Submission

- [ ] **Build Outreach Manager agent**
  When you approve a proposal, the Outreach Manager submits it to Upwork
  via Composio and sets a 3-day follow-up reminder. If no reply after 3 days,
  it drafts a follow-up and sends that to your approval queue too.
  Create: services/api/app/agent/outreach_manager.py
  Use: composio upwork.submit_proposal tool for submission
  Add: follow-up ARQ task scheduled 3 days after submission
  Done when: approved proposal → submitted to real Upwork job → confirmation in Telegram

- [ ] **Set up prompt versioning in PostgreSQL**
  Store every agent prompt in a database table with a version number and
  performance metrics. When you want to improve a prompt, create a new
  version instead of overwriting. This lets you roll back if a new prompt
  performs worse.
  Create: prompt_versions table with columns: agent_type, version, text, win_rate
  Update: agents to load prompts from database instead of hardcoded strings
  Done when: Proposal Writer loads its prompt from the database at runtime

- [ ] **Tag v0.3.0 — Proposals Working**
  Run: git add . && git commit -m "feat: Stage 3 month 3 — Proposals submitting"
       git tag v0.3.0 && git push origin main && git push origin v0.3.0
  Done when: tag visible on GitHub

## MONTH 4, WEEK 1 — Client Communication

- [ ] **Build Client Communicator agent**
  When a client replies to your proposal, this agent handles the response.
  It maintains a professional, warm tone. It never claims to be human if
  asked directly. For anything complex (price negotiations, scope changes,
  complaints) it escalates to your approval queue with a draft response
  for you to review. Conversation history is stored in PostgreSQL.
  Create: services/api/app/agent/client_communicator.py
  Connect: Gmail via Composio for sending/receiving emails
  Done when: client email received → agent drafts response → HITL queue

- [ ] **Build Project Tracker agent**
  When you win a project, the Project Tracker creates a simple project
  record with milestones based on what was agreed in the proposal.
  It sends you a Telegram alert 72 hours before each milestone.
  It generates weekly status update drafts for clients (you approve before sending).
  Create: services/api/app/agent/project_tracker.py
  Create: projects table in PostgreSQL with milestones JSONB column
  Done when: project created → milestones set → 72h warning received in Telegram

- [ ] **Build Finance Manager agent**
  When a project milestone is marked complete, Finance Manager creates
  an invoice from the milestone data (client name, amount, work description,
  bank details). You approve the invoice in the dashboard, then it sends
  to the client via email. Sets a 7-day reminder if no payment received.
  Create: services/api/app/agent/finance_manager.py
  Done when: milestone complete → invoice created → shown in approval queue

## MONTH 4, WEEK 2 — Polish and Tools

- [ ] **Build Simulation Mode (dashboard toggle)**
  A switch in the dashboard that puts the system into testing mode.
  In simulation mode: fake Upwork jobs are generated, fake client personas
  respond to proposals, and all actual sends (Upwork submissions, emails)
  are intercepted and only logged. Metrics are tracked identically.
  Use this to test new agents and prompts without sending anything real.
  Add: [Live] / [Simulation] toggle in dashboard header
  Create: fake job generator and fake client responder using LiteLLM
  Done when: toggle to Simulation → Lead Scout finds fake jobs → no real submissions

- [ ] **Add pgvector-based semantic search (optional, replaces Qdrant)**
  If you are running on 8GB RAM and Qdrant is using too much memory,
  install the pgvector PostgreSQL extension and move vector storage there.
  One fewer service to manage. Switch back to Qdrant when you exceed
  10,000 document chunks (pgvector gets slower at that scale).
  Only do this if RAM is a problem — otherwise keep Qdrant.
  Run: CREATE EXTENSION vector in PostgreSQL
  Replace: qdrant_client calls with pgvector queries
  Done when: semantic search works through PostgreSQL without Qdrant running

- [ ] **Build the client portal page**
  A simple read-only web page for clients to check their project status.
  The URL contains an HMAC-signed token so no login is needed. Shows:
  project name, current milestone, completion percentage, and recent updates.
  Create: apps/web/src/app/portal/[token]/page.tsx
  Create: GET /v1/portal/{token} API endpoint
  Done when: project created → portal URL generated → client sees status page

- [ ] **Set up prompt quality CI with GitHub Actions**
  When you modify any agent prompt, a GitHub Actions workflow runs
  automatically. It tests the new prompt against a set of golden examples
  using DeepEval and reports whether it improved or regressed. This prevents
  you from accidentally deploying a worse prompt.
  Create: .github/workflows/prompt-quality.yml
  Create: evaluation/prompts/test_proposal_writer.py with DeepEval tests
  Done when: PR changing a prompt → GitHub Actions posts evaluation results

## MONTH 4, WEEK 3 — Research and Improvement

- [ ] **Build Research Agent v1 (GitHub + HuggingFace scanning)**
  A weekly agent that scans GitHub Trending (AI/agents category) and
  HuggingFace for new models relevant to Co-Op. It uses the local LLM
  to score relevance (0-10). For anything scoring above 7 it runs a
  quick benchmark in a Docker sandbox and sends you a Telegram message
  with the result and a recommendation.
  Create: services/api/app/agent/research_agent.py
  Add: research_agent cron weekly (Sunday 9pm) in worker.py
  Done when: weekly Telegram message received with real GitHub/HF discovery

- [ ] **Build Docker sandbox for code execution**
  A simple secure code runner using Docker. Creates a temporary container,
  runs the code inside with network disabled and memory limited, returns
  the output, and destroys the container. Used by Research Agent for
  benchmarking and later by Developer Agent for code testing.
  Create: services/api/app/core/docker_sandbox.py
  Test: run "print('hello')" in Python sandbox → returns "hello"
  Note: add microsandbox (microVM isolation) in Stage 4 when needed
  Done when: code executes inside Docker with no host network access

- [ ] **Full end-to-end revenue test**
  Walk through the complete flow from start to money:
  Lead Scout finds job → you see it in Telegram → Proposal Writer drafts
  → you approve → Outreach Manager submits → client replies → Client
  Communicator responds → you win → Project Tracker creates milestones
  → work gets done → Finance Manager creates invoice → you approve →
  invoice sent → payment received.
  Done when: this full flow has been completed at least once with a real client

- [ ] **Tag v0.4.0 — First Revenue Version**
  Run: git add . && git commit -m "feat: Stage 3 complete — first revenue possible"
       git tag v0.4.0 && git push origin main && git push origin v0.4.0
  Done when: tag visible on GitHub

## MONTH 4, WEEK 4 — Delivery Capability (Optional)

These tasks add code delivery capability. Do them only if you want
to deliver websites or software to clients, not just proposals.

- [ ] **Add code-server to docker-compose.yml (optional)**
  code-server is VS Code running in your browser as a Docker container.
  The Developer Agent writes code into code-server via its API.
  You can review the code in your browser before approving delivery.
  Add to docker-compose.yml:
    code-server:
      image: linuxserver/code-server:latest
      ports: ["8443:8443"]
      volumes: ["code_workspace:/config/workspace"]
  Only add this if you want to deliver actual websites or apps to clients.
  Done when: VS Code accessible at http://localhost:8443

- [ ] **Build Developer Agent (optional)**
  The Developer Agent writes code using code-server and uses Claude or
  GPT-4o (via LiteLLM as external tools, not the agent's brain) for
  complex code generation. It tests code in the Docker sandbox. The
  Quality Reviewer checks the result. You do a final review before delivery.
  Only build this if you are delivering code projects.
  Create: services/api/app/agent/developer_agent.py
  Requires: code-server service running, Composio GitHub integration
  Done when: developer agent creates GitHub repo, writes code, tests pass

---

# ══════════════════════════════════════════════════
# STAGE 4 — ADD FULL V5.3 COMPONENTS
# Add only when you feel the specific pain
# Month 5 onward
# ══════════════════════════════════════════════════

## SCALE UP TRIGGERS AND TASKS

Each section below starts with the TRIGGER — the pain you will feel
that tells you it is time to add this component. Do not add it early.

### WHEN: "ARQ loses tasks when container restarts mid-workflow"

- [ ] **Deploy Temporal workflow engine**
  Temporal stores workflow state in its own PostgreSQL database. Even
  if your container crashes mid-execution, the workflow resumes exactly
  where it left off when the container restarts. Essential for multi-day
  client workflows that must not be interrupted.
  Add to docker-compose.yml: temporal service on port 7233
  Add to docker-compose.yml: temporal-ui service on port 8088
  Migrate: proposal pipeline from ARQ to Temporal workflow
  Done when: Temporal UI at localhost:8088 shows workflow history

- [ ] **Add zombie agent detector**
  A Celery Beat cron that runs every 10 minutes. Checks if any Temporal
  workflow has been running longer than 2x its average duration for that
  type. If yes: pauses LiteLLM calls for that thread, snapshots state,
  alerts Telegram. Prevents a stuck agent from burning your token budget.
  Requires Temporal to be running first.
  Done when: simulated stuck workflow → detected and paused within 10 minutes

### WHEN: "Upwork/scraping keeps getting blocked"

- [ ] **Upgrade Browserless and add proxy rotation**
  Configure Browserless with residential proxies to appear as different
  users from different locations. Upwork and LinkedIn track IP addresses
  and block data center IPs quickly.
  Update: Browserless config with proxy provider credentials
  Done when: Lead Scout runs without block errors for 7 consecutive days

- [ ] **Add scraper abstraction layer in Tool Router**
  When a site changes its HTML structure, you should only need to update
  one file. Create separate executor files per platform (upwork_v1.py,
  upwork_v2.py). When v1 breaks, swap to v2 without changing agent code.
  Create: services/tool-router/executors/ directory
  Done when: switching Upwork scraper version requires changing 1 file only

### WHEN: "I need proper debugging — why did the agent do that?"

- [ ] **Deploy OpenTelemetry + Grafana Tempo**
  OpenTelemetry collects traces from every function call across all
  services. Tempo stores and indexes them. You can then search for
  "what happened in this agent run" and see every step, every LLM call,
  every tool call with timing.
  Add to docker-compose.yml: otel-collector, grafana-tempo, prometheus, grafana
  Instrument: add OTel spans to LangGraph nodes, ARQ tasks
  Done when: Grafana at localhost:3001 shows agent execution traces

### WHEN: "I'm delivering code to clients and Docker sandbox feels risky"

- [ ] **Replace Docker sandbox with microsandbox (microVM isolation)**
  microsandbox uses hardware-level virtualization (libkrun). Each code
  execution gets its own kernel — escaping the sandbox into your host
  system is physically impossible. Essential when you run client-submitted
  or LLM-generated code you do not fully control.
  Requires: KVM enabled on your machine (/dev/kvm must exist)
  Replace: docker_sandbox.py with microsandbox client
  Done when: code runs in microsandbox, coop doctor shows TIER 1 sandbox

### WHEN: "Code tasks take 2+ minutes because npm/pip is slow"

- [ ] **Deploy Verdaccio (local npm cache) and devpi (local PyPI cache)**
  Instead of downloading packages from the internet on every sandbox run,
  keep a local copy. Verdaccio caches npm packages. devpi caches PyPI
  packages. Pre-seed with common packages. Reduces sandbox startup 80%.
  Add to docker-compose.yml: verdaccio on port 4873, devpi on port 3141
  Update: TASK_EGRESS_RULES to route npm_install to localhost:4873
  Done when: npm install in sandbox fetches from localhost instead of internet

### WHEN: "I have 15+ agents and the LLM is a bottleneck at peak hours"

- [ ] **Deploy vLLM (if you have a GPU)**
  vLLM delivers 3x more requests per second than Ollama for the same GPU.
  It uses PagedAttention for efficient memory management. If you have a
  GPU (RTX 3080+) and your agents are queuing, add vLLM.
  Add to docker-compose.yml: vllm service on port 8001
  Update: litellm_config.yaml to route standard+ tasks to vLLM
  Done when: GPU utilization visible in Grafana, response time improves

- [ ] **Alternatively: upgrade to Groq paid API**
  If you do not have a GPU, Groq offers very fast inference at low cost.
  Much simpler than running vLLM. Add your Groq API key to Vault and
  configure LiteLLM to route to Groq when local models are busy.
  Done when: overflow tasks route to Groq when Ollama is busy

### WHEN: "I have complex permission rules for a team of 3+"

- [ ] **Deploy Open Policy Agent (OPA)**
  OPA is a centralized policy engine. You write rules in a simple language
  (Rego) that define exactly which agents can do which actions. This is
  much cleaner than if/else checks in FastAPI code when you have 5+ roles.
  Add to docker-compose.yml: opa service on port 8181
  Create: config/opa_policies/ directory with Rego policy files
  Done when: policy files control tool access, simulated violation is blocked

### WHEN: "Messages are getting lost between services at high load"

- [ ] **Deploy NATS JetStream**
  NATS provides distributed, persistent message queuing. Unlike Redis
  Streams, NATS is designed specifically for high-throughput pub/sub with
  guaranteed delivery across multiple nodes. Switch ARQ to use NATS as
  its broker when Redis starts becoming a bottleneck.
  Add to docker-compose.yml: nats service on port 4222
  Migrate: ARQ broker configuration from Redis to NATS
  Done when: NATS handles all inter-service events, Redis used only for caching

### WHEN: "I have 50+ clients and need relationship intelligence"

- [ ] **Deploy Neo4j for Graphiti memory**
  PostgreSQL JSONB is fine for simple client facts. Neo4j is a graph
  database that makes relationship queries fast: "which clients are in
  the same industry as this new prospect?" and "which proposal style
  works best with UK fintech companies?" Switch when JSONB queries slow down.
  Add to docker-compose.yml: neo4j service on port 7474
  Migrate: client_memory table to Graphiti+Neo4j
  Done when: Graphiti stores client relationship graph, query time < 100ms

### WHEN: "Revenue > £10k/month, need to scale and enterprise features"

- [ ] **Add Traefik API gateway**
  Traefik handles TLS certificates, rate limiting, and request routing.
  Required when going multi-node or exposing the API publicly.
  Add to docker-compose.yml: traefik on ports 80 and 443
  Done when: API accessible via HTTPS, rate limiting active

- [ ] **Add enterprise SSO (Keycloak)**
  Enterprise clients need to log in with their own company credentials
  (Google Workspace, Okta, Azure AD). Keycloak provides OIDC/SAML
  federation so you do not manage passwords.
  Done when: login via Google Workspace SSO → correct dashboard permissions

- [ ] **Set up Helm charts for Kubernetes**
  When you need more than one server for reliability, move to Kubernetes.
  Helm charts define the entire stack as code. This is Stage 4 enterprise.
  Done when: helm install co-op deploys full stack on a Kubernetes cluster

---

# TASK COUNT SUMMARY

| Stage | Tasks | When | Goal |
|-------|-------|------|------|
| Stage 1 | 17 tasks | This week | Working chatbot, v0.1.0 on GitHub |
| Stage 2 | 18 tasks | Month 2 | Real LLM, Telegram, Upwork reading |
| Stage 3 | 27 tasks | Month 3-4 | Proposals submitted, first revenue |
| Stage 4 | 12+ tasks | Month 5+ | Add only when you feel the pain |

Stage 1-3 total: 62 tasks over 4 months.
All of them achievable solo with AI IDE assistance.

---

# HOW TO USE YOUR AI IDE FOR EACH TASK

Before giving a task to Kiro or Antigravity, always:

1. Tell it which stage and task you are on
   "I am working on Stage 2, Week 3, Telegram Bot task"

2. Share the relevant existing files as context
   - services/api/app/main.py
   - services/api/app/config.py
   - infrastructure/docker/docker-compose.yml
   - This task description

3. Give it the exact "Done when" criteria
   "The task is complete when: curl localhost:8000/health returns all ok"

4. Set boundaries for the current stage
   "We are in Stage 2. Do not add Temporal, NATS, OPA, or Neo4j.
    Use ARQ instead of Celery. Use PostgreSQL JSONB instead of Neo4j."

5. Verify the "Done when" before marking the task complete
   Do not trust that code looks correct — run the actual test.

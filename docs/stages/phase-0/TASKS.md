# Co-Op Enterprise AI OS — Task List
> Last updated: Phase 0 near-complete. Backend verified ✅. Frontend rebuilt ✅. Integration fixes in progress.

---

## How to Use This File
- Work through tasks **top to bottom**
- Never start a phase until the previous phase checklist is complete
- Mark tasks `[x]` as you complete them
- Each task has a **Verify** step — only check it off when that step passes

---

## 🔥 IMMEDIATE — Fix Before Anything Else

### Fix 1: Database Migration
- [ ] Run `cd services/api && alembic upgrade head`
- [ ] Verify: `docker exec -it co-op-postgres-1 psql -U coop -d coop -c "\d conversations"` shows `tenant_id` column
- [ ] Verify: No more `column conversations.tenant_id does not exist` in postgres logs

### Fix 2: Docker Environment
- [ ] Open `infrastructure/docker/docker-compose.yml`
- [ ] Confirm `co-op-api` has: `DB_PASS`, `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`, `MINIO_ENDPOINT`, `SECRET_KEY`, `ENVIRONMENT`, `PYTHONPATH`
- [ ] Open `infrastructure/docker/.env` — all values are non-empty
- [ ] Run `docker compose build co-op-api && docker compose up -d`
- [ ] Verify: `docker compose ps` — all containers `Up (healthy)`

### Fix 3: python-multipart
- [ ] Check `services/api/pyproject.toml` has `python-multipart>=0.0.9`
- [ ] If missing, add it and rebuild: `docker compose build co-op-api`
- [ ] Verify: `curl -X POST http://localhost:8000/v1/auth/token -d "username=admin@co-op.local&password=testpass123"` returns a token

### Fix 4: IDE Pyre2 Warnings (optional, IDE only)
- [ ] Update `.vscode/settings.json` with correct `.venv` interpreter path
- [ ] Update `services/api/pyrightconfig.json` with `reportMissingImports: false`

---

## Phase 0 Completion Checklist

### Backend Verification (should all pass already)
- [x] `curl http://localhost:8000/health` → `{status: ok, postgres: ok, redis: ok, qdrant: ok}`
- [x] `POST /v1/auth/token` → JWT token returned
- [x] `POST /v1/documents` (multipart) → document uploaded to MinIO
- [x] Document ingestion: PENDING → INDEXING → READY
- [x] `POST /v1/search` → ranked results with citations
- [x] `POST /v1/chat/stream` → SSE stream: citation → tokens → done

### Frontend Verification
- [ ] `cd apps/web && pnpm build` → zero TypeScript errors
- [ ] `http://localhost:3000` → redirects to `/login`
- [ ] Login with `admin@co-op.local` / `testpass123` → reaches `/dashboard`
- [ ] Dashboard: health dots are green (calls `/health` live)
- [ ] `/documents`: upload a PDF → status changes to READY
- [ ] `/search`: type query → get ranked results with excerpts
- [ ] `/chat`: ask question → SSE streaming response with citations
- [ ] All 10 sidebar nav links work without 404
- [ ] Browser DevTools → zero red console errors
- [ ] Page refresh on any route → no hydration errors

### Push to GitHub
- [ ] `git add .`
- [ ] `git status` → confirm no `.env` files are tracked
- [ ] `git commit -m "feat: Phase 0 complete — full RAG pipeline + dark dashboard frontend"`
- [ ] `git push origin main`
- [ ] Open `https://github.com/NAVANEETHVVINOD/CO_OP` → confirm commit appears
- [ ] Confirm `.env` files are NOT visible in the repo

### Tag Phase 0 Release
- [ ] `git tag v0.1.0 -m "Phase 0 complete: Company GPT working end-to-end"`
- [ ] `git push origin v0.1.0`

---

## Phase 1 — Enterprise Knowledge Platform

> **DO NOT START** until all Phase 0 checklist items above are checked off.

### T-021: Keycloak SSO + RBAC (8 hrs)
- [ ] Add `keycloak` service to `docker-compose.yml` (port 8080)
- [ ] Create Keycloak realm `coop` with OIDC client `coop-api`
- [ ] Configure 6 roles: admin, manager, agent_operator, analyst, viewer, service_account
- [ ] Write setup script `scripts/setup_keycloak.py` that automates realm config via API
- [ ] Update `services/api/app/core/security.py` to validate Keycloak JWTs via JWKS endpoint
- [ ] Update `apps/web` login page to redirect to Keycloak OIDC instead of posting credentials
- [ ] Test: Login via Keycloak → token validated in FastAPI → role-based access works
- [ ] Verify: Admin sees admin panel, viewer gets 403

### T-022: LLM Guard Prompt Security (4 hrs)
- [ ] Add `llm-guard` to `services/api/pyproject.toml`
- [ ] Create `services/api/app/middleware/llm_guard.py` with input/output scanners
- [ ] Add as FastAPI middleware on `/v1/chat` and `/v1/search` routes
- [ ] Input scanners: PromptInjection, Sensitive (PII), Toxicity
- [ ] Output scanners: Deanonymize, Sensitive
- [ ] Log all blocks to `audit_events` table
- [ ] Test: Send `"ignore all instructions"` → returns 400 with block reason
- [ ] Verify: Block appears in audit log

### T-023: Traefik API Gateway + TLS (3 hrs)
- [ ] Add `traefik` service to docker-compose
- [ ] Configure TLS termination (self-signed for dev, Let's Encrypt for prod)
- [ ] Add rate limiting: 100 req/min per IP on `/v1/auth/token`
- [ ] Route `/api/*` → api service, `/*` → web service
- [ ] Test: HTTP redirects to HTTPS
- [ ] Test: 101st request to auth endpoint returns 429

### T-024: RAGFlow Full Document Parsing (6 hrs)
- [ ] Add Excel parsing: `openpyxl` → extract all sheets as structured markdown tables
- [ ] Add PowerPoint parsing: `python-pptx` → extract text per slide with slide number
- [ ] Add scanned PDF OCR: `pytesseract` fallback when pypdf extracts < 100 chars
- [ ] Update `services/api/app/services/parser.py` with all new parsers
- [ ] Test: Upload `.xlsx` → ask `"what was total revenue?"` → correct number returned
- [ ] Test: Upload `.pptx` → ask `"summarize slide 3"` → correct content

### T-025: Temporal Workflow Engine (8 hrs)
- [ ] Add `temporal` and `temporal-ui` services to docker-compose (port 7233, 8088)
- [ ] Add `temporalio` SDK to `services/api/pyproject.toml`
- [ ] Create `DocumentIngestionWorkflow` with 5 activities: fetch, parse, chunk, embed, index
- [ ] Each activity: retry policy 3x, exponential backoff, 120s timeout
- [ ] Replace Redis Stream consumer loop with Temporal worker
- [ ] Test: Kill worker mid-ingestion → restart → document still gets indexed
- [ ] Verify: Temporal UI at `http://localhost:8088` shows workflow history

### T-026: Cross-Encoder Reranker (3 hrs)
- [ ] Verify `cross-encoder/ms-marco-MiniLM-L-6-v2` is in `services/api/app/services/reranker.py`
- [ ] Update `hybrid_search` to pass top-10 results through reranker → return top-5
- [ ] Measure recall improvement vs baseline (should go from 92% → 95%+)
- [ ] Test: Same query as before → better ranked results

### T-027: Admin Panel UI — Phase 1 Features (6 hrs)
- [ ] Build user management in `/admin` → Users tab: list, create, edit role, deactivate
- [ ] Connect to `GET /v1/users` and `PUT /v1/users/{id}` endpoints
- [ ] Add audit log viewer to `/admin` → Logs tab
- [ ] Add document bulk operations (select multiple → delete)
- [ ] Test: Admin creates user → user can login

### T-028: Docker Swarm 3-Node Deploy (4 hrs)
- [ ] Create `docker-compose.swarm.yml` with `deploy` sections
- [ ] Configure: api=3 replicas, web=2 replicas, workers=2 replicas
- [ ] Add Docker Secrets for DB password and JWT key
- [ ] Configure rolling update: parallelism=1, delay=10s, failure_action=rollback
- [ ] Test: `docker stack deploy` → all services Running
- [ ] Load test: 500 concurrent users, P95 < 3s (Locust)

### T-029: Grafana + Prometheus Dashboards (4 hrs)
- [ ] Add `prometheus` and `grafana` services to docker-compose
- [ ] Configure scraping for all services at 15s interval
- [ ] Create Grafana dashboard with 8 golden signals (from Doc 16)
- [ ] Configure alert: P95 > 3s for 5min → Slack notification
- [ ] Verify: All metrics visible in Grafana at `http://localhost:3001`

### T-030: Loki Log Aggregation (2 hrs)
- [ ] Add `loki` and `promtail` services to docker-compose
- [ ] Configure all services to log JSON to stdout
- [ ] Connect Loki as Grafana datasource
- [ ] Verify: Logs searchable in Grafana Explore

### Phase 1 Gate
- [ ] All Phase 1 tasks above complete
- [ ] `pytest` → all tests pass, 80%+ coverage
- [ ] 500-user Locust test: P95 < 3s, error rate < 0.1%
- [ ] Login via Keycloak → works end-to-end
- [ ] Upload Excel with tables → query returns correct cell data
- [ ] Temporal UI shows document workflow history
- [ ] `git tag v0.2.0` and push

---

## Phase 2 — Agent Automation Platform

> **DO NOT START** until Phase 1 gate is complete.

### T-034: LangGraph HITL Interrupt/Resume (8 hrs)
- [ ] Add `interrupt_before=['action_node']` to research agent graph compile
- [ ] When interrupt fires: save to `hitl_approvals` table, publish to Redis Streams
- [ ] Create Temporal signal that pauses workflow waiting for approval
- [ ] Build `POST /v1/approvals/{id}` endpoint (approve/reject with signed JWT)
- [ ] Build `GET /v1/approvals` and `GET /v1/approvals/count`
- [ ] Test: Agent reaches mutating action → HITL inbox shows evidence pack
- [ ] Test: Approve → workflow resumes → tool executes
- [ ] Test: Reject → workflow terminates → rejection logged

### T-035: Composio MCP Gateway (6 hrs)
- [ ] Deploy Composio MCP server as Docker service
- [ ] Connect tools: Slack, Gmail, GitHub, Jira, Google Calendar
- [ ] Build tool access RBAC: viewer cannot trigger email tools
- [ ] All tool calls log to `audit_events`
- [ ] Build Tools section in Admin panel showing OAuth status
- [ ] Test: Agent sends Slack message after HITL approval

### T-036: HITL Approval Inbox UI (5 hrs)
- [ ] Update `/approvals/page.tsx` with real-time approval queue
- [ ] Build `EvidencePack` component (agent reasoning + proposed action)
- [ ] Add WebSocket subscription for real-time notifications
- [ ] Approve button: calls `POST /v1/approvals/{id}` with decision
- [ ] Reject button: shows textarea → calls with rejection note
- [ ] Test: Trigger agent action → approval appears in UI in < 2 seconds

### T-037: Workflow Builder Canvas (10 hrs)
- [ ] Install `@xyflow/react` (React Flow v12)
- [ ] Build `/workflows/page.tsx` — library with create/run/delete
- [ ] Build `/workflows/[id]/page.tsx` — full-screen canvas
- [ ] Custom node types: AgentNode, ToolNode, HITLNode, TriggerNode, ConditionNode
- [ ] Implement workflow save/load via `POST/GET /v1/workflows`
- [ ] Implement run: triggers Temporal workflow, shows live node status
- [ ] Add 5 starter templates
- [ ] Test: Build workflow in UI → run → see live node status updates

### T-039: Kubernetes Helm Charts (8 hrs)
- [ ] Create `infrastructure/helm/co-op-core/` Helm chart
- [ ] Charts for: api, web, ingestion worker, inference
- [ ] Configure HPA: api at 70% CPU, worker at 50% CPU
- [ ] Configure KEDA: workers scale on Redis queue depth > 5
- [ ] Test: `helm install co-op` → all pods Running
- [ ] Load test: 2000 concurrent users, KEDA scales workers

### T-040: KEDA Event-Driven Autoscaling (3 hrs)
- [ ] Install KEDA in Kubernetes cluster
- [ ] Create `ScaledObject` for agent workers: Redis queue trigger
- [ ] Configure min=2, max=10 replicas
- [ ] Test: Push 50 messages to agent queue → workers scale to 8+

### T-041: Promptfoo Red-Team CI (3 hrs)
- [ ] Create `evaluation/promptfoo/config.yaml` with 500+ tests
- [ ] Test categories: prompt injection, jailbreaks, PII extraction, cross-tenant
- [ ] Add to GitHub Actions CI
- [ ] Configure: any successful attack = CI failure
- [ ] Test: Known injection attempt is blocked

### T-042: vLLM GPU Inference (5 hrs)
- [ ] Deploy vLLM with Mixtral 8x7B on GPU node
- [ ] Update `litellm_config.yaml` to add vLLM as second model
- [ ] Configure routing: simple queries → CPU, complex → GPU
- [ ] Benchmark: measure throughput vs Ollama CPU
- [ ] Test: Complex query routes to GPU model

### T-043: Analytics Dashboard (6 hrs)
- [ ] Build `/analytics/page.tsx` with Recharts
- [ ] Charts: cost/day by model, query volume, agent success rate, HITL approval rate
- [ ] Connect to `GET /v1/analytics/cost` and `/v1/analytics/usage`
- [ ] Add CSV export for finance team
- [ ] Test: Cost dashboard shows real data from cost_events table

### Phase 2 Gate
- [ ] All Phase 2 tasks complete
- [ ] 2000-user Locust test: P95 < 2s
- [ ] Agent HITL flow works end-to-end: propose → approve → execute
- [ ] Workflow builder: create, save, run a workflow
- [ ] Zero successful Promptfoo attacks
- [ ] `git tag v0.3.0` and push

---

## Phase 3 — Enterprise AI OS

> **DO NOT START** until Phase 2 gate is complete.

| Task | Description | Est |
|------|-------------|-----|
| T-047 Graphiti Memory | Temporal knowledge graph for agent long-term memory | 10h |
| T-048 HashiCorp Vault | Dynamic secrets, zero static credentials | 6h |
| T-049 Istio Ambient | mTLS all service traffic, traffic policies | 8h |
| T-050 CrewAI Teams | Multi-agent pipelines (research→draft→review) | 8h |
| T-051 A2A Protocol | Cross-organization agent federation | 6h |
| T-052 KubeRay GPU | Distributed GPU auto-scaling for vLLM | 10h |
| T-053 Multi-region K8s | 3-region active-active Kubernetes | 10h |
| T-054 Disaster Recovery | WAL-G backups, Velero, RTO < 1hr | 5h |
| T-055 SOC2 Type II | Evidence collection, audit package | 15h |
| T-056 GDPR/CCPA | Right-to-erasure, data retention policies | 5h |

### Phase 3 Gate
- [ ] All Phase 3 tasks complete
- [ ] Graphiti: agent recalls fact from 3 weeks ago correctly
- [ ] Vault: zero hardcoded/static secrets anywhere in codebase
- [ ] Istio: all traffic mTLS verified in Kiali
- [ ] SOC2 evidence package compiled
- [ ] `git tag v0.4.0` and push

---

## Phase 4 — Full Production

> **DO NOT START** until Phase 3 gate is complete.

| Task | Description | Est |
|------|-------------|-----|
| T-057 MLflow Registry | Model versioning, experiment tracking | 6h |
| T-058 Tauri Desktop | macOS/Windows/Linux app, offline RAG | 10h |
| T-059 Agent Marketplace | 15+ community templates, install UI | 8h |
| T-060 Penetration Test | External firm, OWASP LLM Top 10 | 20h |
| T-061 SRE Runbooks | Incident response, PagerDuty on-call | 8h |
| T-062 C-Suite Analytics | ROI dashboards, productivity metrics | 6h |
| T-063 White-label | Custom branding per tenant | 5h |
| T-064 API Docs | OpenAPI, SDK docs, integration guide | 6h |
| T-065 Chaos Engineering | Chaos Mesh monthly drills | 5h |
| T-066 Cost Optimization | $0.005/query target, GPU routing tuning | 4h |
| T-067 Onboarding Flow | First-run wizard, in-app tour | 6h |
| T-068 HIPAA Compliance | Healthcare tenant support | 10h |

### Phase 4 Gate (v1.0.0 Release)
- [ ] 10,000 concurrent users at P95 < 2s
- [ ] External pen test: zero critical/high findings unresolved
- [ ] Chaos Mesh: 99.99%+ uptime during 1hr chaos test
- [ ] Agent marketplace: 15+ templates installable
- [ ] SOC2 Type II certificate issued
- [ ] `git tag v1.0.0` and push
- [ ] Publish to GitHub with full documentation and demo video

---

## Quick Reference: What To Do RIGHT NOW

```
1. Run: docker compose up -d
2. Check: docker compose ps → all healthy
3. Run: cd services/api && alembic upgrade head
4. Check: curl http://localhost:8000/health
5. Run: cd apps/web && pnpm build
6. Fix: any TypeScript errors from build
7. Test: open http://localhost:3000 → login → dashboard
8. Push: git add . && git commit -m "..." && git push origin main
9. Tag: git tag v0.1.0 && git push origin v0.1.0
10. Start Phase 1: T-021 Keycloak
```

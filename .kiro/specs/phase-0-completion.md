# Phase 0 Completion — Bug Fixes & GitHub Push

## Metadata
- **Status**: Draft
- **Priority**: Critical
- **Phase**: 0
- **Estimated Time**: 2-3 hours
- **Dependencies**: None (backend already working)

---

## Overview

Complete Phase 0 of Co-Op Enterprise AI OS by fixing three critical integration bugs, verifying the full stack works end-to-end, and pushing the working code to GitHub with a v0.1.0 release tag.

The backend RAG pipeline is fully working and verified. The frontend dark dashboard UI is built. Three bugs prevent end-to-end integration. This spec fixes those bugs in order, verifies the complete system, and delivers the first release.

---

## Requirements

### Functional Requirements

**FR-1: Docker Environment Configuration**
- All environment variables must be passed to co-op-api service
- API container must start without crashes
- All services (postgres, redis, qdrant, minio, api, web) must reach healthy state

**FR-2: Database Schema Completeness**
- All Alembic migrations must be applied
- `conversations` table must have `tenant_id` column
- API endpoints must not return 500 errors due to missing columns

**FR-3: Authentication Dependencies**
- `python-multipart` must be installed in API container
- OAuth2 form-based authentication must work
- POST /v1/auth/token must return JWT tokens

**FR-4: Frontend Build Quality**
- TypeScript build must complete with zero errors
- No `any` types in production code
- All imports must resolve correctly

**FR-5: End-to-End User Flow**
- Login flow: redirect to /login → authenticate → reach /dashboard
- Document upload: PDF → status PENDING → INDEXING → READY
- Search: query → ranked results with excerpts and citations
- Chat: question → SSE streaming response with citation cards
- All 10 navigation links must work without 404 errors
- Browser console must show zero red errors

**FR-6: Git Repository Hygiene**
- No `.env` files committed to repository
- No `.venv` or `__pycache__` directories committed
- `.gitignore` must prevent sensitive files from being staged

**FR-7: GitHub Release**
- Code pushed to main branch
- v0.1.0 tag created with release message
- Repository visible at https://github.com/NAVANEETHVVINOD/CO_OP

### Non-Functional Requirements

**NFR-1: No Backend Code Changes**
- Do NOT modify any Python files in `services/api/app/` except:
  - Adding dependency to `pyproject.toml` (Bug 3)
  - Running Alembic migrations (Bug 2)
- Backend is working and verified — only fix configuration issues

**NFR-2: Phase Discipline**
- Fix ONLY Phase 0 bugs
- Do NOT add Phase 1 services (Keycloak, Temporal, LLM Guard, Traefik)
- Do NOT add Phase 2 features (Kubernetes, Composio MCP, HITL full flow)

**NFR-3: No Placeholders**
- Every file must be complete and working
- No `// TODO` comments
- No stub functions that return null/undefined

**NFR-4: Docker Service Names**
- Use `postgres`, `redis`, `qdrant`, `minio` (NOT `localhost`) in Docker configs
- Only use `localhost` for host machine access

---

## Design

### Bug 1 Fix: Docker Environment Variables

**Problem**: API container crashes with `DB_PASS Field required` error because environment variables are not passed from docker-compose to the FastAPI application.

**Root Cause**: The `co-op-api` service in `infrastructure/docker/docker-compose.yml` is missing environment variable declarations.

**Solution**: Add complete environment block to `co-op-api` service.

**File**: `infrastructure/docker/docker-compose.yml`

**Changes**:
```yaml
co-op-api:
  build:
    context: ../../services/api
    dockerfile: Dockerfile
  ports:
    - "8000:8000"
  environment:
    DATABASE_URL: postgresql+asyncpg://coop:${DB_PASS}@postgres:5432/coop
    DB_PASS: ${DB_PASS}
    REDIS_URL: redis://redis:6379
    QDRANT_URL: http://qdrant:6333
    MINIO_URL: minio:9000
    MINIO_ENDPOINT: minio:9000
    MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
    MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
    MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
    SECRET_KEY: ${SECRET_KEY}
    ENVIRONMENT: development
    PYTHONPATH: /app
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
    qdrant:
      condition: service_started
    minio:
      condition: service_healthy
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 15s
    timeout: 5s
    retries: 5
```

**Verification**:
```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
docker compose -f infrastructure/docker/docker-compose.yml ps
# All services should show "Up (healthy)"
curl http://localhost:8000/health
# Should return: {"status":"ok","postgres":"ok","redis":"ok","qdrant":"ok"}
```

---

### Bug 2 Fix: Database Migration

**Problem**: API returns 500 error on `/v1/chat/conversations` with message `column conversations.tenant_id does not exist`.

**Root Cause**: Alembic migration `14e1dfdf2a5b_add_tenant_id_to_conversations.py` exists but has not been applied to the database.

**Solution**: Run Alembic upgrade inside the API container.

**Command**:
```bash
cd services/api
alembic upgrade head
```

**Alternative** (if running in Docker):
```bash
docker exec co-op-api alembic upgrade head
```

**Verification**:
```bash
# Check migration status
docker exec co-op-api alembic current

# Verify column exists
docker exec -it co-op-postgres-1 psql -U coop -d coop -c "\d conversations"
# Should show tenant_id column

# Test endpoint
curl -H "Authorization: Bearer <token>" http://localhost:8000/v1/chat/conversations
# Should return [] (empty array), not 500 error
```

---

### Bug 3 Fix: Missing Python Dependency

**Problem**: API startup fails or auth endpoint returns error because `python-multipart` is not installed. FastAPI's `OAuth2PasswordRequestForm` requires this package.

**Root Cause**: `python-multipart` is missing from `services/api/pyproject.toml` dependencies.

**Solution**: Add dependency and rebuild Docker image.

**File**: `services/api/pyproject.toml`

**Changes**: Verify this line exists in the `dependencies` array:
```toml
"python-multipart>=0.0.9",
```

**Note**: This dependency already appears to be present in the current `pyproject.toml`. If the error persists, rebuild the Docker image:

```bash
docker compose -f infrastructure/docker/docker-compose.yml build co-op-api
docker compose -f infrastructure/docker/docker-compose.yml up -d co-op-api
```

**Verification**:
```bash
# Test auth endpoint with form data
curl -X POST http://localhost:8000/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@co-op.local&password=testpass123"

# Should return:
# {"access_token":"<jwt>","token_type":"bearer","expires_in":900}
```

---

### Task 4 Design: Frontend Build Verification

**Objective**: Ensure TypeScript compilation succeeds with zero errors.

**Process**:
1. Install dependencies: `cd apps/web && pnpm install`
2. Run build: `pnpm build`
3. Fix any TypeScript errors:
   - No `any` types
   - All imports resolve
   - All props interfaces defined
   - Strict mode compliance

**Common Issues**:
- Missing type imports from `@/types/api`
- Incorrect prop types in components
- Missing return types on functions
- Unused variables (remove or prefix with `_`)

**Verification**:
```bash
cd apps/web
pnpm build
# Exit code should be 0
# Output should show: "Compiled successfully"
```

---

### Task 5 Design: End-to-End UI Testing

**Test Sequence**:

1. **Login Flow**
   - Navigate to http://localhost:3000
   - Should redirect to /login
   - Enter: `admin@co-op.local` / `testpass123`
   - Click "Sign In"
   - Should redirect to /dashboard

2. **Dashboard Health Check**
   - Dashboard should show health status indicators
   - All health dots should be green (postgres, redis, qdrant, minio)
   - No loading spinners stuck

3. **Document Upload**
   - Navigate to /documents
   - Click upload button
   - Select a PDF file
   - Document should appear with status "PENDING"
   - Status should change to "INDEXING" then "READY" (may take 10-60 seconds)

4. **Search Functionality**
   - Navigate to /search
   - Enter a query related to uploaded document
   - Should see ranked results with:
     - Document filename
     - Relevance score
     - Text excerpt
     - Page number

5. **Chat Interface**
   - Navigate to /chat
   - Type a question related to uploaded document
   - Should see:
     - Citation cards appear first (event: citation)
     - Streaming text response (event: token)
     - "Done" indicator (event: done)
   - Response should reference the document with page numbers

6. **Navigation Test**
   - Click each sidebar link:
     - Dashboard ✓
     - Chat ✓
     - Documents ✓
     - Search ✓
     - Agents ✓
     - Approvals ✓
     - Admin ✓
   - All pages should load without 404 errors

7. **Console Check**
   - Open browser DevTools → Console tab
   - Should see zero red errors
   - Warnings are acceptable
   - Network tab should show successful API calls

**Verification Checklist**:
```
[ ] Login redirects to dashboard
[ ] Dashboard shows green health indicators
[ ] Document upload works, status changes to READY
[ ] Search returns results with excerpts
[ ] Chat streams response with citations
[ ] All 10 sidebar links work
[ ] Zero red console errors
```

---

### Task 6 Design: Git Ignore Verification

**Objective**: Ensure sensitive files are not committed to repository.

**File**: `.gitignore` (root)

**Required Entries** (verify these exist):
```gitignore
# Python
services/api/.venv/
services/api/.pytest_cache/
services/api/__pycache__/
services/api/test.db
services/api/uploads/
**/__pycache__/
**/*.pyc
*.egg-info/

# Node
apps/web/node_modules/
apps/web/.next/
node_modules/

# Docker
infrastructure/docker/.env

# IDE
.vscode/settings.json
.turbo/

# Root env
.env

# Misc
*.log
.DS_Store
```

**Verification**:
```bash
git status
# Should NOT show:
# - .env files
# - .venv directories
# - __pycache__ directories
# - node_modules directories
# - .next directory
```

---

### Task 7 Design: GitHub Push & Release

**Objective**: Push working code to GitHub and create v0.1.0 release tag.

**Prerequisites**:
- All bugs fixed (Tasks 1-3)
- Frontend builds successfully (Task 4)
- End-to-end tests pass (Task 5)
- .gitignore verified (Task 6)

**Commands**:
```bash
# Stage all changes
git add .

# Verify no sensitive files staged
git status
# Check output carefully - should NOT see .env files

# Commit
git commit -m "feat: Phase 0 complete — full RAG pipeline + dark dashboard frontend

- Fixed Docker environment variable configuration
- Applied database migrations (tenant_id column)
- Verified python-multipart dependency
- Frontend build passing with zero TypeScript errors
- End-to-end flow tested: login → upload → search → chat
- All 10 pages working without errors

Backend verified:
✅ RAG pipeline: upload → parse → chunk → embed → Qdrant
✅ Hybrid search: BM25 + dense vectors, RRF merge
✅ LangGraph research agent: retrieve → rerank → generate
✅ SSE streaming chat with citation events
✅ JWT auth + PostgreSQL + Redis + MinIO + Qdrant

Frontend verified:
✅ Dark dashboard UI with 10 pages
✅ Document upload with status tracking
✅ Knowledge search with ranked results
✅ Chat interface with SSE streaming
✅ All navigation links working
✅ Zero console errors"

# Push to main
git push origin main

# Create release tag
git tag v0.1.0 -m "Phase 0: Company GPT working end-to-end

First release of Co-Op Enterprise AI OS.

Features:
- Self-hosted RAG pipeline (PDF/DOCX/TXT/MD support)
- Hybrid search (BM25 + dense vectors)
- LangGraph research agent
- SSE streaming chat with citations
- JWT authentication
- Dark dashboard UI
- 6 Docker services: API, Web, PostgreSQL, Redis, Qdrant, MinIO

Deployment:
- Docker Compose (Phase 0)
- No GPU required
- No LLM API keys required (stubbed inference)

Test credentials:
- Email: admin@co-op.local
- Password: testpass123"

# Push tag
git push origin v0.1.0
```

**Verification**:
```bash
# Check remote
git remote -v
# Should show: origin  https://github.com/NAVANEETHVVINOD/CO_OP.git

# Verify commit pushed
git log origin/main -1
# Should show your commit

# Verify tag pushed
git ls-remote --tags origin
# Should show: refs/tags/v0.1.0

# Open in browser
open https://github.com/NAVANEETHVVINOD/CO_OP
# Should see:
# - Latest commit visible
# - v0.1.0 tag in releases
# - No .env files visible in file browser
```

---

## Tasks

### Task 1: Fix Docker Environment Variables
**Priority**: Critical
**Estimated Time**: 15 minutes

**Steps**:
1. Open `infrastructure/docker/docker-compose.yml`
2. Locate the `co-op-api` service definition
3. Add complete `environment` block with all required variables
4. Save file
5. Restart Docker services: `docker compose -f infrastructure/docker/docker-compose.yml up -d`
6. Check container status: `docker compose -f infrastructure/docker/docker-compose.yml ps`
7. Verify health endpoint: `curl http://localhost:8000/health`

**Acceptance Criteria**:
- [ ] All Docker containers show "Up (healthy)" status
- [ ] API container does not crash loop
- [ ] Health endpoint returns `{"status":"ok","postgres":"ok","redis":"ok","qdrant":"ok"}`
- [ ] No "DB_PASS Field required" errors in logs

**Verification Command**:
```bash
docker compose -f infrastructure/docker/docker-compose.yml logs co-op-api --tail 50
# Should NOT show "DB_PASS Field required" error
```

---

### Task 2: Apply Database Migrations
**Priority**: Critical
**Estimated Time**: 5 minutes

**Steps**:
1. Ensure Docker services are running (Task 1 complete)
2. Run: `cd services/api && alembic upgrade head`
   - OR: `docker exec co-op-api alembic upgrade head`
3. Verify migration applied: `docker exec co-op-api alembic current`
4. Check database schema: `docker exec -it co-op-postgres-1 psql -U coop -d coop -c "\d conversations"`
5. Test conversations endpoint with auth token

**Acceptance Criteria**:
- [ ] Alembic reports current revision as `14e1dfdf2a5b` (or latest)
- [ ] `conversations` table has `tenant_id` column
- [ ] GET /v1/chat/conversations returns `[]` (empty array), not 500 error
- [ ] No "column conversations.tenant_id does not exist" errors in logs

**Verification Command**:
```bash
# Get auth token first
TOKEN=$(curl -s -X POST http://localhost:8000/v1/auth/token \
  -d "username=admin@co-op.local&password=testpass123" | jq -r .access_token)

# Test conversations endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/v1/chat/conversations
# Should return: []
```

---

### Task 3: Verify Python Dependencies
**Priority**: Critical
**Estimated Time**: 10 minutes

**Steps**:
1. Open `services/api/pyproject.toml`
2. Verify `"python-multipart>=0.0.9"` exists in dependencies array
3. If missing, add it and rebuild: `docker compose -f infrastructure/docker/docker-compose.yml build co-op-api`
4. Restart API service: `docker compose -f infrastructure/docker/docker-compose.yml up -d co-op-api`
5. Test auth endpoint with form data

**Acceptance Criteria**:
- [ ] `python-multipart>=0.0.9` present in pyproject.toml
- [ ] Docker image builds successfully
- [ ] POST /v1/auth/token with form data returns JWT token
- [ ] No "python-multipart not installed" errors

**Verification Command**:
```bash
curl -X POST http://localhost:8000/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@co-op.local&password=testpass123"

# Should return:
# {"access_token":"eyJ...","token_type":"bearer","expires_in":900}
```

---

### Task 4: Verify Frontend Build
**Priority**: High
**Estimated Time**: 20 minutes

**Steps**:
1. Navigate to frontend: `cd apps/web`
2. Install dependencies: `pnpm install`
3. Run build: `pnpm build`
4. Review any TypeScript errors
5. Fix errors (if any):
   - Add missing type imports
   - Fix `any` types
   - Add missing prop interfaces
   - Fix unused variables
6. Re-run build until successful

**Acceptance Criteria**:
- [ ] `pnpm install` completes without errors
- [ ] `pnpm build` exits with code 0
- [ ] Build output shows "Compiled successfully"
- [ ] Zero TypeScript errors
- [ ] No `any` types in production code

**Verification Command**:
```bash
cd apps/web
pnpm build
echo "Exit code: $?"
# Should show: Exit code: 0
```

---

### Task 5: End-to-End UI Testing
**Priority**: High
**Estimated Time**: 30 minutes

**Steps**:
1. Ensure all services running (Tasks 1-3 complete)
2. Open browser to http://localhost:3000
3. Execute test sequence (see Design section above):
   - Login flow
   - Dashboard health check
   - Document upload
   - Search functionality
   - Chat interface
   - Navigation test
   - Console check
4. Document any issues found
5. Fix issues and re-test

**Acceptance Criteria**:
- [ ] Login redirects to /dashboard after authentication
- [ ] Dashboard shows green health indicators for all services
- [ ] Document upload works, status progresses to READY
- [ ] Search returns ranked results with excerpts and scores
- [ ] Chat streams response with citation cards
- [ ] All 10 sidebar navigation links work without 404
- [ ] Browser console shows zero red errors

**Test Checklist**:
```
Login Flow:
[ ] http://localhost:3000 redirects to /login
[ ] Login form accepts admin@co-op.local / testpass123
[ ] Successful login redirects to /dashboard

Dashboard:
[ ] Health indicators visible
[ ] All health dots are green
[ ] No stuck loading states

Documents:
[ ] Upload button works
[ ] PDF file uploads successfully
[ ] Status shows PENDING → INDEXING → READY

Search:
[ ] Search input accepts query
[ ] Results display with scores
[ ] Excerpts show relevant text
[ ] Page numbers visible

Chat:
[ ] Chat input accepts message
[ ] Citation cards appear
[ ] Response streams token by token
[ ] Done indicator appears

Navigation:
[ ] Dashboard link works
[ ] Chat link works
[ ] Documents link works
[ ] Search link works
[ ] Agents link works
[ ] Approvals link works
[ ] Admin link works

Console:
[ ] Zero red errors in DevTools console
[ ] Network requests succeed (200/201 status)
```

---

### Task 6: Verify Git Ignore
**Priority**: Medium
**Estimated Time**: 5 minutes

**Steps**:
1. Open `.gitignore` in root directory
2. Verify all required entries present (see Design section)
3. Run `git status`
4. Check output for any sensitive files
5. If sensitive files appear, add patterns to .gitignore
6. Run `git status` again to verify

**Acceptance Criteria**:
- [ ] `.gitignore` contains all required patterns
- [ ] `git status` does NOT show .env files
- [ ] `git status` does NOT show .venv directories
- [ ] `git status` does NOT show __pycache__ directories
- [ ] `git status` does NOT show node_modules directories

**Verification Command**:
```bash
git status | grep -E '\\.env|venv|__pycache__|node_modules|\\.next'
# Should return empty (no matches)
```

---

### Task 7: Push to GitHub & Create Release
**Priority**: Medium
**Estimated Time**: 15 minutes

**Steps**:
1. Verify all previous tasks complete
2. Stage changes: `git add .`
3. Review staged files: `git status`
4. Commit with detailed message (see Design section)
5. Push to main: `git push origin main`
6. Create annotated tag: `git tag v0.1.0 -m "..."`
7. Push tag: `git push origin v0.1.0`
8. Verify on GitHub web interface

**Acceptance Criteria**:
- [ ] `git status` shows no .env files before commit
- [ ] Commit pushed to origin/main successfully
- [ ] Tag v0.1.0 created and pushed
- [ ] GitHub repository shows latest commit
- [ ] GitHub releases page shows v0.1.0 tag
- [ ] No .env files visible in GitHub file browser

**Verification Commands**:
```bash
# Check remote
git remote -v

# Verify commit
git log origin/main -1

# Verify tag
git tag -l
git ls-remote --tags origin

# Open in browser
open https://github.com/NAVANEETHVVINOD/CO_OP
```

---

## Success Criteria

Phase 0 is complete when ALL of the following are true:

### Technical Success Criteria
- [ ] All 6 Docker services healthy (postgres, redis, qdrant, minio, api, web)
- [ ] Health endpoint returns all services "ok"
- [ ] Database migrations applied, no missing columns
- [ ] Auth endpoint returns JWT tokens
- [ ] Frontend builds with zero TypeScript errors
- [ ] Document upload → indexing → ready flow works
- [ ] Search returns ranked results with citations
- [ ] Chat streams responses with SSE events
- [ ] All 10 pages accessible without 404 errors
- [ ] Browser console shows zero red errors

### Repository Success Criteria
- [ ] Code pushed to https://github.com/NAVANEETHVVINOD/CO_OP
- [ ] Tag v0.1.0 visible in releases
- [ ] No .env files committed
- [ ] No .venv directories committed
- [ ] README visible (if exists)

### Documentation Success Criteria
- [ ] Commit message describes Phase 0 completion
- [ ] Tag message lists key features
- [ ] Test credentials documented

---

## Constraints & Rules

### Critical Constraints (NEVER VIOLATE)

1. **NO API KEYS**: Do not add Ollama, OpenAI, Claude, or any LLM API configuration
2. **NO BACKEND CHANGES**: Do not modify Python files except pyproject.toml dependency
3. **PHASE DISCIPLINE**: Do not add Phase 1+ services (Keycloak, Temporal, LLM Guard, Traefik)
4. **NO PLACEHOLDERS**: Every file must be complete, no TODOs or stubs
5. **DOCKER HOSTNAMES**: Use service names (postgres, redis, qdrant, minio) not localhost
6. **PROTECT useChat.ts**: Never rewrite `apps/web/src/hooks/useChat.ts` — it works
7. **COMPLETE FILES**: Always show full file contents when making changes
8. **ENV VARS ONLY**: Never hardcode passwords, secrets, or connection strings

### What to Ask Before Doing

- Dropping or recreating database tables
- Changing RAG pipeline logic
- Modifying useChat.ts
- Adding new Docker services
- Changing authentication logic
- Upgrading major library versions

### What to Never Do

- Delete production data
- Change Qdrant collection schema
- Add LLM API key configuration
- Move to Phase 1+ services

---

## Notes

### Test Credentials
```
Email: admin@co-op.local
Password: testpass123
Tenant: co-op (auto-created)
```

### Service URLs
```
Frontend:  http://localhost:3000
API:       http://localhost:8000
API Docs:  http://localhost:8000/docs
Postgres:  localhost:5433 (mapped from 5432)
Redis:     localhost:6379
Qdrant:    http://localhost:6333
MinIO API: http://localhost:9000
MinIO UI:  http://localhost:9001
```

### Common Commands
```bash
# Start all services
docker compose -f infrastructure/docker/docker-compose.yml up -d

# Check status
docker compose -f infrastructure/docker/docker-compose.yml ps

# View logs
docker compose -f infrastructure/docker/docker-compose.yml logs co-op-api -f

# Restart API
docker compose -f infrastructure/docker/docker-compose.yml restart co-op-api

# Rebuild API
docker compose -f infrastructure/docker/docker-compose.yml build co-op-api
docker compose -f infrastructure/docker/docker-compose.yml up -d co-op-api

# Run migrations
docker exec co-op-api alembic upgrade head

# Frontend dev
cd apps/web && pnpm dev

# Frontend build
cd apps/web && pnpm build
```

---

## Review Checklist

Before starting implementation, verify:

- [ ] All required files have been read and understood
- [ ] Bug fixes are clearly defined with exact file changes
- [ ] Task order is logical (bugs first, then verification, then push)
- [ ] Acceptance criteria are measurable and specific
- [ ] No Phase 1+ work included in this spec
- [ ] All constraints documented and understood
- [ ] Success criteria cover both technical and repository goals

---

**Ready for Review**: Please review this spec before I begin implementation. Let me know if you'd like any changes to the requirements, design, or task order.

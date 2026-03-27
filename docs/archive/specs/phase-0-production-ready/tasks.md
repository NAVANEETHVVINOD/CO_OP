# Implementation Plan: Phase 0 Production Ready

## Overview

This implementation plan converts the Phase 0 Production Ready design into executable coding tasks. The plan is organized into 4 major parts with 37 discrete tasks. Each task builds on previous work and includes specific requirements references for traceability.

The backend RAG pipeline is fully functional and verified. This plan focuses on fixing three critical integration bugs, completing the frontend rebuild with all 10 pages (including 11 major UI improvements), verifying the complete system works end-to-end, and publishing the first production release to GitHub.

**11 Major UI Improvements:**
1. Dashboard: 3-column layout with sparklines and hardcoded activity data
2. AppSidebar: "CO_OP / GATEWAY DASHBOARD" branding with 4 sections
3. TopBar: Breadcrumb navigation and health pill polling
4. Chat: Two-panel layout with conversation management
5. Documents: Drag-drop with XHR progress and slide-over drawer
6. Search: Filter row with mode toggle and query highlighting
7. Agents: 3 agent cards with Run Agent modal
8. Approvals: Full Phase 2 preview with HITL inbox UI
9. Admin: shadcn Tabs with Users | System | About
10. StatusDot/StatusBadge: Expanded prop types for all statuses
11. Auth + UX: Token refresh, loading skeletons, error toasts, conversation loading

## Tasks

### Part 1: Bug Fixes and Backend Verification

- [x] 1. Fix Docker environment variable configuration
  - Verify all environment variables are present in docker-compose.yml co-op-api service
  - Confirm .env file in infrastructure/docker/ contains DB_PASS, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, SECRET_KEY
  - Test that API container starts without "DB_PASS Field required" errors
  - Verify all 6 services reach healthy state
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  - _Verification: `docker compose -f infrastructure/docker/docker-compose.yml ps` shows all services "Up (healthy)"_

- [ ] 2. Apply database migration for tenant_id column
  - Execute Alembic migration 14e1dfdf2a5b_add_tenant_id_to_conversations
  - Verify conversations table has tenant_id column with UUID type and foreign key constraint
  - Test GET /v1/chat/conversations endpoint returns array without 500 errors
  - Confirm no "column conversations.tenant_id does not exist" errors in logs
  - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - _Verification: `docker exec co-op-api alembic current` shows 14e1dfdf2a5b_

- [ ] 3. Verify python-multipart dependency
  - Confirm python-multipart>=0.0.9 exists in services/api/pyproject.toml
  - Rebuild Docker image if dependency was missing
  - Test POST /v1/auth/token with form-urlencoded data
  - Verify response includes access_token, token_type, and expires_in fields
  - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - _Verification: Authentication endpoint returns valid JWT token_

- [ ] 4. Verify health endpoint functionality
  - Test GET /health endpoint returns 200 status code
  - Verify all service fields (postgres, redis, qdrant, minio) return "ok"
  - Confirm overall status field is "ok"
  - Test /ready endpoint returns 200 when all services healthy
  - _Requirements: 1.4_
  - _Verification: `curl http://localhost:8000/health` returns all services "ok"_

- [ ] 5. Verify authentication endpoint with test credentials
  - Test authentication flow with admin@co-op.local / testpass123
  - Verify JWT token structure includes sub, exp, tenant_id claims
  - Test protected endpoint /v1/auth/me with Bearer token
  - Confirm token is valid for 900 seconds
  - _Requirements: 3.2, 3.3, 3.4, 5.2_
  - _Verification: Token authentication works end-to-end_

- [ ] 6. Checkpoint - Ensure all backend services are healthy
  - Ensure all tests pass, ask the user if questions arise.

### Part 2: Frontend Complete Rebuild

- [x] 7. Verify design system in globals.css
  - Confirm all CSS variables defined (--bg-base, --bg-surface, --bg-elevated, etc.)
  - Verify custom animations (pulse-dot, blink-cursor, spin-custom, fade-in, slide-right)
  - Check utility classes (.section-label, .card, .nav-item-active, .btn-primary, .mono-id)
  - Ensure dark theme colors match Co-Op Gateway Dashboard design
  - _Requirements: 4.1, 4.2, 4.3_
  - _Verification: File exists with all variables and animations defined_

- [x] 8. Verify Tailwind configuration
  - Confirm tailwind.config.ts maps all color tokens to CSS variables
  - Verify font families configured (Inter, JetBrains Mono)
  - Check tailwindcss-animate plugin included
  - Ensure no TypeScript errors in config file
  - _Requirements: 4.1, 4.2, 4.3_
  - _Verification: Tailwind config compiles without errors_

- [x] 9. Verify TypeScript API types
  - Confirm all interfaces defined in apps/web/src/types/api.ts
  - Check Document, Conversation, Message, Citation, SearchResult, AgentRun, HealthResponse interfaces
  - Verify all fields have correct types and optional fields marked with ?
  - Ensure no `any` types used
  - _Requirements: 4.3, 4.4_
  - _Verification: All API types match backend response structures_

- [x] 10. Verify API client library
  - Confirm apiFetch wrapper handles auth and token refresh in apps/web/src/lib/api.ts
  - Check typed helpers: getDocuments, uploadDocument, deleteDocument, searchDocuments
  - Verify automatic Bearer token injection from localStorage
  - Test redirect to /login on auth failure
  - _Requirements: 5.2, 10.2_
  - _Verification: API client handles authentication correctly_

- [x] 11. Verify Zustand chat store
  - Confirm store defined in apps/web/src/store/chatStore.ts
  - Check all state fields: messages, isGenerating
  - Verify all actions: addMessage, appendTokenToLastMessage, appendCitationToLastMessage, setGenerating, clearMessages, setMessages
  - Ensure no TypeScript errors
  - _Requirements: 8.1, 8.2, 8.3, 8.4_
  - _Verification: Chat store compiles and exports correct interface_

- [x] 12. Verify StatusDot component (IMPROVEMENT 10)
  - Confirm component in apps/web/src/components/shared/StatusDot.tsx
  - Check status prop accepts 'healthy' | 'ok' | 'error' | 'warning' | 'pending' | 'unknown'
  - Verify backward compatibility: 'ok' maps to 'healthy', 'pending' maps to 'warning'
  - Verify size variants (sm, md) and pulse animation
  - Test color classes: healthy=green, error=red, warning=amber, unknown=gray
  - _Requirements: 5.4_
  - _Verification: Component renders with correct colors and animations for all 6 status types_

- [x] 13. Verify StatusBadge component (IMPROVEMENT 10)
  - Confirm component in apps/web/src/components/shared/StatusBadge.tsx
  - Check status prop accepts 'READY' | 'PENDING' | 'INDEXING' | 'FAILED' | 'running' | 'completed' | 'pending' | 'failed'
  - Verify document statuses: READY=green, PENDING/INDEXING=amber with pulse, FAILED=red
  - Verify agent statuses: running=blue with pulse, completed=green, pending=amber, failed=red
  - Test pill-shaped badge styling with fallback for unknown statuses
  - _Requirements: 6.2_
  - _Verification: Component renders all document and agent status badges correctly_

- [x] 14. Verify MonoId component
  - Confirm component in apps/web/src/components/shared/MonoId.tsx
  - Check truncated UUID display with maxLength prop
  - Verify copy-to-clipboard functionality
  - Test checkmark appears on copy
  - _Requirements: 9.2_
  - _Verification: Component truncates IDs and copies to clipboard_

- [x] 15. Verify EmptyState component
  - Confirm component in apps/web/src/components/shared/EmptyState.tsx
  - Check icon, title, description, and optional action props
  - Verify centered layout with proper spacing
  - Test action button onClick handler
  - _Requirements: 9.4_
  - _Verification: Component displays empty states correctly_

- [x] 16. Verify PageHeader component
  - Confirm component in apps/web/src/components/shared/PageHeader.tsx
  - Check title, optional description, and optional action props
  - Verify flex layout with space-between
  - Test action slot renders correctly
  - _Requirements: 9.2_
  - _Verification: Component renders page headers correctly_

- [x] 17. Implement AppSidebar component (IMPROVEMENT 2)
  - Create apps/web/src/components/layout/AppSidebar.tsx
  - Implement logo: "CO_OP" bold 18px + "GATEWAY DASHBOARD" 9px muted uppercase with letter-spacing
  - Add four sections: KNOWLEDGE, AUTOMATION, ANALYTICS, SETTINGS
  - KNOWLEDGE: Dashboard, Chat, Documents, Search
  - AUTOMATION: Agents, Approvals
  - ANALYTICS: Analytics (Phase 2, opacity-50 with gray pill badge)
  - SETTINGS: Admin
  - Implement active state highlighting with left border accent and background
  - Add bottom user card with avatar, email (admin@co-op.local), and Settings link
  - _Requirements: 9.1, 9.2_
  - _Verification: Sidebar renders with logo, 4 sections, Phase 2 items marked, user card at bottom_

- [ ] 18. Implement TopBar component (IMPROVEMENT 3)
  - Create apps/web/src/components/layout/TopBar.tsx
  - Implement 52px height header with three sections
  - LEFT: Breadcrumb navigation from usePathname() showing current page path
  - RIGHT: Health pill (polls /health every 30s) + Bell icon + User avatar
  - Health pill shows green/red StatusDot with "Healthy"/"Issues" text
  - Breadcrumb converts pathname to readable format (e.g., /dashboard → Dashboard)
  - _Requirements: 5.4_
  - _Verification: TopBar displays breadcrumb, health pill polls every 30s, bell and avatar buttons work_

- [x] 19. Implement Login page
  - Create apps/web/src/app/(auth)/login/page.tsx
  - Implement form with email and password inputs
  - Submit to POST /v1/auth/token with form-urlencoded data
  - Store JWT token in localStorage on success
  - Redirect to /dashboard after successful login
  - Display error toast on failure
  - _Requirements: 3.2, 5.1, 5.2_
  - _Verification: Login flow works with test credentials admin@co-op.local / testpass123_

- [x] 20. Implement root page redirect
  - Create apps/web/src/app/page.tsx
  - Check for token in localStorage
  - Redirect to /dashboard if token exists
  - Redirect to /login if no token
  - Show loading spinner during redirect
  - _Requirements: 5.1_
  - _Verification: Root page redirects correctly based on auth state_

- [x] 21. Implement app layout with auth guard
  - Create apps/web/src/app/(app)/layout.tsx
  - Check for token on mount, redirect to /login if missing
  - Render AppSidebar and TopBar for authenticated users
  - Implement scrollable main content area
  - Show loading spinner during auth check
  - _Requirements: 5.1, 5.2, 9.1_
  - _Verification: Layout guards protected routes and renders sidebar/topbar_

- [x] 22. Implement Dashboard page (IMPROVEMENT 1)
  - Create apps/web/src/app/(app)/dashboard/page.tsx
  - Implement 3-column grid layout: LEFT (col-span-2) + RIGHT (col-span-1)
  - LEFT COLUMN: Three stat cards with sparklines (Documents, Chunks Indexed, Queries Today) + Recent Activity table
  - Sparklines: 12 data points showing visual trend with flex-1 bars
  - Recent Activity: Hardcoded 5 rows with type icon, query text, user email, timestamp
  - RIGHT COLUMN: System Snapshot card + Recent Documents card + Agent Run Monitor card
  - System Snapshot: Health status for postgres, redis, qdrant, minio with StatusDot indicators
  - Recent Documents: Top 3 documents with filename, status badge, chunk count
  - Agent Run Monitor: Research Agent (active) + 2 Phase 2 agents (opacity-50)
  - _Requirements: 5.3, 5.4, 9.2_
  - _Verification: Dashboard displays 3-column layout with all cards, hardcoded activity data, sparklines_

- [ ] 23. Implement Chat page (IMPROVEMENT 4)
  - Create apps/web/src/app/(app)/chat/page.tsx and ChatPage.tsx
  - Implement two-panel layout: LEFT (260px conversations list) + RIGHT (flex-1 messages area)
  - LEFT PANEL: "New Chat" button + conversations list with selection state
  - RIGHT PANEL: Messages area + citation cards + streaming cursor + input area
  - Verify uses existing useChat.ts hook (DO NOT MODIFY useChat.ts)
  - Citation cards display above assistant messages with source, page, score
  - Streaming indicator shows animated cursor (animate-blink-cursor) during generation
  - Input area with send button, disabled during generation
  - Conversation selection loads message history
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 14.4_
  - _Verification: Chat interface has two-panel layout, conversation management, streaming with citations_

- [ ] 24. Implement Documents page (IMPROVEMENT 5)
  - Create apps/web/src/app/(app)/documents/page.tsx
  - Implement drag-drop upload zone with visual feedback (border-accent on drag)
  - Use XHR (XMLHttpRequest) for upload with progress tracking via xhr.upload.addEventListener('progress')
  - Display progress bar during upload showing percentage
  - Implement polling with Set<string> tracking PENDING/INDEXING document IDs, poll every 2 seconds
  - Display document table with filename, type, status, chunks, created date, delete button
  - Implement slide-over drawer (320px from right) on row click showing document details
  - Drawer shows: filename, ID (MonoId), status badge, file type, file size, chunks, created date, error message
  - Delete button with confirmation dialog
  - Show empty state when no documents
  - _Requirements: 6.1, 6.2, 6.4, 9.2, 9.4_
  - _Verification: Drag-drop works, XHR progress tracks upload, polling updates status, drawer shows details_

- [ ] 25. Implement Search page (IMPROVEMENT 6)
  - Create apps/web/src/app/(app)/search/page.tsx
  - Implement search input with submit button
  - Add filter row with two controls: Results dropdown (All/High Relevance/Medium Relevance) + Mode toggle (Semantic/Balanced/Keyword)
  - Results dropdown shows count for each filter level
  - Mode toggle uses button group with active state highlighting
  - Implement query term highlighting using <mark> tags with bg-accent/30
  - Add "Use in Chat →" button on each result that stores context in sessionStorage
  - Display results with source filename, page number, relevance score, highlighted text excerpt
  - Show empty state before search and when no results found
  - Implement loading state during search
  - Display result count
  - _Requirements: 7.1, 7.2, 9.2, 9.4_
  - _Verification: Search has filter row, mode toggle, query highlighting, "Use in Chat" button works_

- [ ] 26. Implement Agents page (IMPROVEMENT 7)
  - Create apps/web/src/app/(app)/agents/page.tsx
  - Display 3 agent cards: Research Agent (active), Support Agent (Phase 2), Code Agent (Phase 2)
  - Each card shows: agent icon, name, Phase 2 badge (if applicable), status dot, description, last run time, "Run Agent" button
  - Phase 2 agents have opacity-50 and disabled button
  - Implement "Run Agent" modal with status tracker showing idle/running/completed/failed states
  - Modal shows: agent type, status with StatusDot and pulse animation, progress indicator during run
  - Add Recent Runs table with columns: Run ID (MonoId), Agent, Status (StatusBadge), Started, Duration
  - Populate Recent Runs with 3 hardcoded example runs
  - _Requirements: 9.2, 9.4, 13.1, 13.2_
  - _Verification: Page displays 3 agent cards, Run Agent modal works, Recent Runs table shows history_

- [ ] 27. Implement Approvals page (IMPROVEMENT 8)
  - Create apps/web/src/app/(app)/approvals/page.tsx
  - Display empty state with green CheckCircle icon (w-16 h-16 in green/20 circle)
  - Show title "No pending approvals" and description about HITL workflow
  - Add info card (bg-accent/5 border-accent/20) explaining HITL approvals for Phase 2
  - Info card includes: AlertCircle icon, title, description, 4 bullet points about HITL features
  - Add "Phase 2 Preview" section with example approval card (opacity-60 pointer-events-none)
  - Preview card shows: Proposed Action header, Agent type, timestamp, PENDING badge
  - Include Evidence section with 3 items (FileText icons + text)
  - Include Parameters section with JSON display in monospace font
  - Include Approve/Reject buttons (green/red with ThumbsUp/ThumbsDown icons)
  - _Requirements: 9.2, 9.4, 13.1, 13.2_
  - _Verification: Page displays empty state, info card, full Phase 2 preview with approval UI_

- [ ] 28. Implement Admin page (IMPROVEMENT 9)
  - Create apps/web/src/app/(app)/admin/page.tsx
  - Implement shadcn Tabs component with 3 tabs: Users | System | About
  - USERS TAB: Display user table with columns: Email, Role, Tenant, Status
  - Show 1 hardcoded user: admin@co-op.local, admin role, co-op tenant, active status
  - SYSTEM TAB: Display 4 stat cards (Users, Tenants, Documents, Conversations) + 3 info cards
  - Info cards: Environment (development/production), Services (6 services with health status), Configuration (API URL, Phase, Version)
  - ABOUT TAB: Display technology grid with 12 technologies (Next.js, React, Tailwind, FastAPI, Python, LangGraph, PostgreSQL, Redis, Qdrant, MinIO, Docker, TypeScript)
  - Each technology shows: name, version, category badge
  - Add Phase 1 Preview section listing 8 upcoming features
  - _Requirements: 9.2_
  - _Verification: Admin page has 3 tabs, Users table, System cards, About grid, all data displays correctly_

- [ ] 29. Checkpoint - Ensure frontend build passes
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 29A. Implement Auth Token Refresh (IMPROVEMENT 11)
  - Update apps/web/src/lib/api.ts apiFetch function
  - Add 401 response handler that attempts token refresh
  - Call /v1/auth/refresh endpoint with refresh token from localStorage
  - Store new access token and retry original request with new token
  - Redirect to /login if refresh fails or no refresh token available
  - Remove both tokens from localStorage on refresh failure
  - _Requirements: 5.2, 10.2_
  - _Verification: Token refresh works on 401, automatic retry succeeds, redirect on failure_

- [ ] 29B. Implement Loading Skeletons (IMPROVEMENT 11)
  - Create apps/web/src/components/shared/LoadingSkeleton.tsx
  - Implement DashboardSkeleton matching 3-column layout with animated pulse
  - Implement DocumentsSkeleton with 5 table row skeletons
  - Implement SearchSkeleton with 3 result card skeletons
  - Implement ChatSkeleton with two-panel layout (conversations + messages)
  - Use skeletons in all major pages during initial data loading
  - Apply animate-pulse class and bg-elevated for skeleton elements
  - _Requirements: 10.1, 10.4_
  - _Verification: All pages show loading skeletons before data loads, smooth transitions_

- [ ] 29C. Setup Error Toast Notifications (IMPROVEMENT 11)
  - Update apps/web/src/app/layout.tsx to include Toaster component
  - Configure Toaster with position="top-right" and dark theme styling
  - Apply custom toast styles matching design system (bg-surface, border-dim, text-primary)
  - Add toast.error() calls to all API error handlers across pages
  - Add toast.success() calls for successful operations (upload, delete, etc.)
  - Add toast.loading() for long-running operations with ID tracking
  - _Requirements: 10.1, 10.4_
  - _Verification: Toaster configured, error toasts appear on failures, success toasts on completions_

- [ ] 29D. Implement Conversation History Loading (IMPROVEMENT 11)
  - Update apps/web/src/app/(app)/chat/ChatPage.tsx
  - Add loadConversations() function calling getConversations() API
  - Add loadMessages(conversationId) function calling getConversationMessages() API
  - Implement loading state for initial conversations fetch
  - Implement loadingMessages state for message history fetch
  - Show ChatSkeleton during initial load
  - Display error toast on conversation or message load failure
  - Load messages when user selects conversation from list
  - _Requirements: 8.1, 10.1_
  - _Verification: Conversations load on mount, messages load on selection, error toasts on failures_

### Part 3: Verification

- [ ] 30. Run TypeScript build verification
  - Execute `cd apps/web && pnpm build`
  - Verify build completes with exit code 0
  - Confirm zero TypeScript type errors
  - Check all 10 pages compile successfully
  - Verify no `any` types in production code
  - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - _Verification: Build output shows "Compiled successfully" with all routes listed_

- [ ] 31. Perform end-to-end browser verification
  - Test service health: all 6 Docker services show "Up (healthy)"
  - Test authentication flow: login with admin@co-op.local / testpass123, redirect to /dashboard
  - Test dashboard: verify 4 stat cards and system health indicators display
  - Test document upload: upload PDF, verify status progression PENDING → INDEXING → READY
  - Test search: submit query, verify results with source, page, score, excerpt
  - Test chat: send message, verify citation cards and streaming response
  - Test navigation: click all sidebar links, verify no 404 errors, refresh pages without errors
  - Test empty states: verify agents and approvals pages show Phase 2 messages
  - Test admin panel: verify stats, configuration, and Phase 1 preview display
  - Test console quality: verify ZERO red error messages in browser console
  - _Requirements: 1.3, 1.4, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.4, 7.1, 7.2, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4_
  - _Verification: All 10 test sections pass with zero console errors_

- [ ] 32. Checkpoint - Ensure all verification tests pass
  - Ensure all tests pass, ask the user if questions arise.

### Part 4: GitHub Push

- [ ] 34. Commit, tag, and release to GitHub (IMPROVEMENT 11 - Updated commit message)
  - Verify git status shows no .env files staged or untracked
  - Stage all changes with `git add .`
  - Commit with message: "feat: Phase 0 v0.1.0 - Production ready with 11 UI improvements"
  - Commit body includes: Dashboard 3-col layout, AppSidebar branding, TopBar breadcrumb, Chat 2-panel, Documents drag-drop XHR, Search filters, Agents 3-cards, Approvals Phase 2 preview, Admin tabs, StatusDot/Badge expanded, Auth refresh + loading skeletons + error toasts + conversation loading
  - Create annotated tag v0.1.0 with release notes including features, deployment instructions, test credentials, and quick start guide
  - Push to main branch: `git push origin main`
  - Push tag: `git push origin v0.1.0`
  - Verify on GitHub: commit visible, tag in releases section, no sensitive files in repository
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 12.1, 12.2, 12.3, 12.4, 12.5_
  - _Verification: v0.1.0 tag visible at https://github.com/NAVANEETHVVINOD/CO_OP/releases_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP (none in this plan - all tasks required)
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- All tasks are executable by a coding agent without manual intervention
- Backend Python files should NOT be modified except for dependency verification in pyproject.toml
- The useChat.ts hook is working correctly and must NOT be rewritten
- All Docker service hostnames must use service names (postgres, redis, qdrant, minio) not localhost
- No LLM API keys should be added - system uses stubbed inference
- Phase discipline: only Phase 0 services (no Keycloak, Temporal, LLM Guard, Traefik, RAGFlow)

## Critical Constraints

1. **NO API KEYS**: Do not add Ollama, OpenAI, Claude, or any LLM API configuration
2. **NO BACKEND CHANGES**: Do not modify Python files except pyproject.toml dependency verification
3. **PHASE DISCIPLINE**: Do not add Phase 1+ services (Keycloak, Temporal, LLM Guard, Traefik)
4. **NO PLACEHOLDERS**: Every file must be complete, no TODOs or stubs
5. **DOCKER HOSTNAMES**: Use service names (postgres, redis, qdrant, minio) not localhost in Docker configs
6. **PROTECT useChat.ts**: Never rewrite `apps/web/src/hooks/useChat.ts` — it works correctly
7. **COMPLETE FILES**: Always show full file contents when making changes
8. **ENV VARS ONLY**: Never hardcode passwords, secrets, or connection strings

## Test Credentials

```
Email:    admin@co-op.local
Password: testpass123
Tenant:   co-op (auto-created)
```

## Service URLs

```
Frontend:       http://localhost:3000
API:            http://localhost:8000
API Docs:       http://localhost:8000/docs
Postgres:       localhost:5433 (mapped from 5432)
Redis:          localhost:6379
Qdrant:         http://localhost:6333
Qdrant UI:      http://localhost:6333/dashboard
MinIO API:      http://localhost:9000
MinIO Console:  http://localhost:9001
```

## Common Commands

```bash
# Start all services
docker compose -f infrastructure/docker/docker-compose.yml up -d

# Check service status
docker compose -f infrastructure/docker/docker-compose.yml ps

# Run database migrations
docker exec co-op-api alembic upgrade head

# Frontend build
cd apps/web && pnpm build

# Test health endpoint
curl http://localhost:8000/health | jq

# Test authentication
curl -X POST http://localhost:8000/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@co-op.local&password=testpass123" | jq
```

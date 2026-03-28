# Requirements Document

## Introduction

This document specifies the requirements for completing Phase 0 of the Co-Op Enterprise AI Operating System to make it production-ready for the initial v0.1.0 release. The backend RAG pipeline is fully working and verified. Three critical integration bugs prevent end-to-end functionality. This feature will fix those bugs, verify the complete system works end-to-end, and deliver the first production release to GitHub.

## Glossary

- **Co-Op_System**: The Co-Op Enterprise AI Operating System consisting of frontend, backend API, and infrastructure services
- **RAG_Pipeline**: Retrieval-Augmented Generation pipeline that processes documents through parsing, chunking, embedding, and indexing
- **Docker_Environment**: The Docker Compose orchestration of 6 services (API, Web, PostgreSQL, Redis, Qdrant, MinIO)
- **SSE_Stream**: Server-Sent Events streaming protocol for real-time chat responses
- **Alembic**: Database migration tool for PostgreSQL schema changes
- **JWT_Token**: JSON Web Token for authentication
- **Health_Endpoint**: API endpoint that reports status of all infrastructure services
- **Tenant**: Multi-tenant isolation unit in the database schema
- **HITL**: Human-in-the-Loop approval workflow (Phase 2 feature, empty state in Phase 0)

## Requirements

### Requirement 1: Docker Service Configuration

**User Story:** As a developer, I want all Docker services to start successfully with proper environment configuration, so that the Co-Op system runs without crashes.

#### Acceptance Criteria

1. WHEN the Docker Compose file is executed, THE Docker_Environment SHALL pass all required environment variables to the co-op-api service
2. THE Docker_Environment SHALL include DATABASE_URL, DB_PASS, REDIS_URL, QDRANT_URL, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, SECRET_KEY, ENVIRONMENT, and PYTHONPATH variables
3. WHEN all services start, THE Docker_Environment SHALL reach healthy state for all 6 services within 60 seconds
4. THE Health_Endpoint SHALL return status "ok" for postgres, redis, qdrant, and minio services
5. WHEN the co-op-api service starts, THE Co-Op_System SHALL NOT log "DB_PASS Field required" errors

### Requirement 2: Database Schema Completeness

**User Story:** As a developer, I want all database migrations applied, so that API endpoints do not fail with missing column errors.

#### Acceptance Criteria

1. WHEN Alembic upgrade is executed, THE Alembic SHALL apply migration 14e1dfdf2a5b_add_tenant_id_to_conversations
2. THE conversations table SHALL include a tenant_id column of type UUID with foreign key constraint
3. WHEN GET /v1/chat/conversations is called with valid JWT_Token, THE Co-Op_System SHALL return an array response without 500 errors
4. THE Co-Op_System SHALL NOT log "column conversations.tenant_id does not exist" errors in PostgreSQL logs

### Requirement 3: Authentication Dependencies

**User Story:** As a user, I want to authenticate with username and password, so that I can access protected API endpoints.

#### Acceptance Criteria

1. THE Co-Op_System SHALL include python-multipart version 0.0.9 or higher in the API service dependencies
2. WHEN POST /v1/auth/token receives form-urlencoded data with username and password, THE Co-Op_System SHALL return a JWT_Token with access_token, token_type, and expires_in fields
3. THE JWT_Token SHALL be valid for 900 seconds
4. WHEN authentication succeeds with admin@co-op.local and testpass123, THE Co-Op_System SHALL return a valid JWT_Token

### Requirement 4: Frontend Build Quality

**User Story:** As a developer, I want the frontend to build without TypeScript errors, so that the application can be deployed to production.

#### Acceptance Criteria

1. WHEN pnpm build is executed in apps/web directory, THE Co-Op_System SHALL complete compilation with exit code 0
2. THE Co-Op_System SHALL NOT produce any TypeScript type errors during build
3. THE Co-Op_System SHALL resolve all import statements without module not found errors
4. THE Co-Op_System SHALL NOT use any "any" types in production code paths

### Requirement 5: User Authentication Flow

**User Story:** As a user, I want to log in to the system, so that I can access the dashboard and protected features.

#### Acceptance Criteria

1. WHEN a user navigates to http://localhost:3000 without a JWT_Token, THE Co-Op_System SHALL redirect to /login
2. WHEN a user submits valid credentials on /login, THE Co-Op_System SHALL store the JWT_Token and redirect to /dashboard
3. WHEN a user with valid JWT_Token accesses /dashboard, THE Co-Op_System SHALL display health status indicators for all services
4. THE Co-Op_System SHALL display green status indicators when all services report "ok" from Health_Endpoint

### Requirement 6: Document Upload and Indexing

**User Story:** As a user, I want to upload PDF documents, so that I can search and chat with their content.

#### Acceptance Criteria

1. WHEN a user uploads a PDF file via /documents page, THE Co-Op_System SHALL create a document record with status "PENDING"
2. WHEN the RAG_Pipeline processes the document, THE Co-Op_System SHALL transition status from PENDING to INDEXING to READY
3. THE RAG_Pipeline SHALL complete document processing within 60 seconds for documents under 10MB
4. WHEN document status is READY, THE Co-Op_System SHALL have indexed all document chunks in Qdrant with embeddings

### Requirement 7: Knowledge Search

**User Story:** As a user, I want to search uploaded documents, so that I can find relevant information quickly.

#### Acceptance Criteria

1. WHEN a user submits a search query on /search page, THE Co-Op_System SHALL return ranked results within 2 seconds
2. THE Co-Op_System SHALL return results with content excerpts, relevance scores, source filenames, and page numbers
3. THE Co-Op_System SHALL use hybrid search combining BM25 and dense vector similarity
4. THE Co-Op_System SHALL rerank results using cross-encoder model before returning top results

### Requirement 8: Chat with Streaming Responses

**User Story:** As a user, I want to ask questions and receive streaming responses with citations, so that I can interact naturally with the knowledge base.

#### Acceptance Criteria

1. WHEN a user submits a chat message on /chat page, THE Co-Op_System SHALL stream responses using SSE_Stream protocol
2. THE SSE_Stream SHALL emit citation events before token events
3. THE SSE_Stream SHALL emit token events containing response content
4. THE SSE_Stream SHALL emit a done event with conversation_id and cost_usd after response completion
5. WHEN the RAG_Pipeline retrieves relevant documents, THE Co-Op_System SHALL include citation cards with source filename, page number, and relevance score

### Requirement 9: Navigation Completeness

**User Story:** As a user, I want all navigation links to work, so that I can access all features of the system.

#### Acceptance Criteria

1. THE Co-Op_System SHALL provide 10 accessible pages: login, signup, dashboard, chat, documents, search, agents, approvals, admin, and root redirect
2. WHEN a user clicks any sidebar navigation link, THE Co-Op_System SHALL navigate to the target page without 404 errors
3. WHEN a user refreshes any page while authenticated, THE Co-Op_System SHALL render the page without hydration errors
4. THE Co-Op_System SHALL display empty state components for pages without data (agents, approvals)

### Requirement 10: Browser Console Quality

**User Story:** As a developer, I want zero console errors in production, so that the application runs cleanly without warnings.

#### Acceptance Criteria

1. WHEN a user navigates through all pages, THE Co-Op_System SHALL NOT log any red error messages to browser console
2. WHEN API requests are made, THE Co-Op_System SHALL receive 200 or 201 status codes for successful operations
3. WHEN SSE_Stream connections are established, THE Co-Op_System SHALL NOT log connection errors
4. THE Co-Op_System SHALL handle network errors gracefully with user-visible error messages

### Requirement 11: Repository Security

**User Story:** As a developer, I want sensitive files excluded from version control, so that secrets are not exposed in the public repository.

#### Acceptance Criteria

1. THE Co-Op_System SHALL include a .gitignore file that excludes .env files from all directories
2. THE Co-Op_System SHALL exclude .venv, __pycache__, node_modules, and .next directories from version control
3. WHEN git status is executed, THE Co-Op_System SHALL NOT show any .env files as staged or untracked
4. THE Co-Op_System SHALL exclude .pytest_cache, .turbo, and IDE-specific files from version control

### Requirement 12: GitHub Release

**User Story:** As a project maintainer, I want to publish the v0.1.0 release to GitHub, so that users can access the production-ready code.

#### Acceptance Criteria

1. WHEN all bugs are fixed and tests pass, THE Co-Op_System SHALL be committed to the main branch with a descriptive commit message
2. THE Co-Op_System SHALL be tagged with v0.1.0 annotated tag including release notes
3. THE v0.1.0 tag SHALL be pushed to https://github.com/NAVANEETHVVINOD/CO_OP
4. WHEN viewing the GitHub repository, THE Co-Op_System SHALL display the v0.1.0 tag in the releases section
5. THE GitHub repository SHALL NOT contain any .env files in the file browser

### Requirement 13: Phase Discipline

**User Story:** As a developer, I want to maintain phase boundaries, so that Phase 0 remains stable and focused.

#### Acceptance Criteria

1. THE Co-Op_System SHALL include only Phase 0 services: co-op-api, co-op-web, postgres, redis, qdrant, and minio
2. THE Co-Op_System SHALL NOT include Phase 1 services: Keycloak, Temporal, LLM Guard, Traefik, or RAGFlow
3. THE Co-Op_System SHALL NOT include Phase 2 services: Kubernetes, Composio MCP, or HITL full workflow
4. THE Co-Op_System SHALL use stubbed inference without requiring Ollama, OpenAI, or Claude API keys

### Requirement 14: Backend Stability

**User Story:** As a developer, I want to preserve working backend code, so that verified functionality is not broken.

#### Acceptance Criteria

1. THE Co-Op_System SHALL NOT modify Python files in services/api/app/ except for adding dependencies to pyproject.toml
2. THE Co-Op_System SHALL NOT modify the RAG_Pipeline logic in services/api/app/services/
3. THE Co-Op_System SHALL NOT modify the LangGraph agent implementation in services/api/app/agent/
4. THE Co-Op_System SHALL NOT modify apps/web/src/hooks/useChat.ts

### Requirement 15: Configuration Correctness

**User Story:** As a developer, I want Docker services to use correct hostnames, so that inter-service communication works reliably.

#### Acceptance Criteria

1. WHEN configuring DATABASE_URL, THE Co-Op_System SHALL use hostname "postgres" not "localhost"
2. WHEN configuring REDIS_URL, THE Co-Op_System SHALL use hostname "redis" not "localhost"
3. WHEN configuring QDRANT_URL, THE Co-Op_System SHALL use hostname "qdrant" not "localhost"
4. WHEN configuring MINIO_ENDPOINT, THE Co-Op_System SHALL use hostname "minio" not "localhost"
5. WHERE external access from host machine is needed, THE Co-Op_System SHALL use localhost with mapped ports

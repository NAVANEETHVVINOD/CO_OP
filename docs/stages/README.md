# Co-Op OS Development Stages

This directory organizes documentation by development phase, following the incremental growth strategy from 6 services to full enterprise architecture.

## Stage Structure

```
phase-0/  → Foundation (6 services) - CURRENT PHASE ✅
phase-1/  → Real Intelligence (8 services) - NEXT
phase-2/  → Working Agents (12 services) - FUTURE
phase-3/  → Enterprise Scale (29 services) - FUTURE
```

## Current Phase: Phase 0 (Foundation)

**Status**: Complete ✅ (v1.0.3)

**Services**: 6
- co-op-api (FastAPI backend)
- co-op-web (Next.js frontend)
- postgres (PostgreSQL database)
- redis (Redis cache)
- qdrant (Vector search)
- minio (Object storage)

**What Works**:
- Document upload and RAG pipeline
- Search with citations
- Chat with streaming responses
- Authentication and multi-tenancy
- Health monitoring

**Documentation**: See `phase-0/` directory

## Phase 1: Real Intelligence

**Services**: +2 (ollama, litellm)

**Goals**:
- Real LLM responses (not stubbed)
- Telegram control panel
- Lead Scout agent
- Background task workers
- Token limit enforcement

**Documentation**: See `phase-1/` directory

## Phase 2: Working Agents

**Services**: +4 (browserless, vault, llm-guard, communication)

**Goals**:
- Proposal Writer agent
- Client Communicator
- Project Tracker
- Finance Manager
- HITL approval system

**Documentation**: See `phase-2/` directory

## Phase 3: Enterprise Scale

**Services**: Add as needed (Temporal, Keycloak, Traefik, etc.)

**Goals**:
- Workflow orchestration
- Advanced security
- Observability
- High availability
- Multi-region deployment

**Documentation**: See `phase-3/` directory

## Navigation

- **Current work**: Start in `phase-0/`
- **Planning next phase**: Review `phase-1/`
- **Long-term roadmap**: See `phase-2/` and `phase-3/`
- **Architecture overview**: See `.kiro/steering/architecture.md`
- **Project status**: See `.kiro/steering/project.md`

## Development Philosophy

> "Never add a service unless you feel the pain of not having it."

Each phase builds on the previous one. Complete Phase 0 before starting Phase 1. Complete Phase 1 before starting Phase 2. And so on.

This incremental approach ensures:
- Working software at every stage
- Clear validation checkpoints
- Manageable complexity
- Revenue before scale

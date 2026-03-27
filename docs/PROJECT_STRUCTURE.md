# Co-Op OS Project Structure

This document provides a comprehensive overview of the Co-Op OS project structure, explaining the purpose of each directory and how to navigate the codebase.

## Quick Navigation

- [Root Structure](#root-structure)
- [Documentation (.kiro/ and docs/)](#documentation-kiro-and-docs)
- [Services (services/)](#services-servicesapi)
- [Applications (apps/)](#applications-appsweb)
- [Infrastructure (infrastructure/)](#infrastructure-infrastructuredocker)
- [CLI (cli/)](#cli-cli)
- [Development Workflow](#development-workflow)

## Root Structure

```
co-op/
├── .github/              # GitHub Actions workflows and CI/CD
├── .kiro/                # Kiro IDE configuration and specs
├── apps/                 # Frontend applications
├── cli/                  # Command-line interface
├── docs/                 # Project documentation
├── infrastructure/       # Docker and deployment configs
├── packages/             # Shared packages (future)
├── scripts/              # Utility scripts
├── services/             # Backend services
├── .env                  # Root environment variables
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore patterns
├── package.json          # Root package.json (Turborepo)
├── pnpm-workspace.yaml   # PNPM workspace configuration
└── turbo.json            # Turborepo configuration
```

## Documentation (.kiro/ and docs/)

### .kiro/ - Kiro IDE Configuration

```
.kiro/
├── hooks/                # Agent hooks for automation
├── settings/             # IDE settings
├── specs/                # Feature specifications
│   ├── production-readiness-v1/
│   │   ├── requirements.md
│   │   ├── design.md
│   │   ├── tasks.md
│   │   └── .config.kiro
│   └── ...
└── steering/             # Project steering files
    ├── architecture.md   # System architecture
    ├── constraints.md    # Development constraints
    └── project.md        # Project status and overview
```

**Purpose**: Configuration for Kiro AI IDE, including specs for feature development and steering files for project guidance.

**Key Files**:
- `.kiro/steering/architecture.md` - 10-layer architecture overview
- `.kiro/steering/project.md` - Current phase status, environment variables
- `.kiro/steering/constraints.md` - Hard rules and constraints
- `.kiro/specs/production-readiness-v1/` - Current production readiness spec


### docs/ - Project Documentation

```
docs/
├── archive/              # Historical documentation
│   ├── 2026-03-27_*.md   # Archived docs with date prefix
│   └── README.md         # Archive index
├── rules/                # AI IDE constraint files (.mdc)
│   ├── co-op-agent-behavior.mdc
│   ├── co-op-api-contracts.mdc
│   ├── co-op-coding-standards.mdc
│   ├── co-op-critical-constraints.mdc
│   ├── co-op-file-structure.mdc
│   ├── co-op-phase1.mdc
│   ├── co-op-project-overview.mdc
│   ├── co-op-solo-guidelines.mdc
│   ├── PROJECT.mdc
│   ├── Rule1.mdc
│   └── TASK.mdc
└── stages/               # Phase-specific documentation
    ├── phase-0/          # Current phase (Stage 1 - Foundation)
    │   ├── DEVELOPMENT.md
    │   ├── INSTALL.md
    │   ├── PROJECT.md
    │   ├── TASKS.md
    │   ├── USAGE.md
    │   └── stage1_implementation.md
    ├── phase-1/          # Stage 2 - Real Intelligence
    │   └── stage2_implementation.md
    ├── phase-2/          # Stage 3 - Working Agents
    │   └── stage3_implementation.md
    ├── phase-3/          # Stage 4 - Enterprise Scale
    │   └── stage4_implementation.md
    └── README.md         # Stages overview
```

**Purpose**: All project documentation organized by phase and purpose.

**Key Files**:
- `docs/stages/phase-0/` - Current phase documentation
- `docs/stages/README.md` - Development stages overview
- `docs/rules/*.mdc` - AI IDE constraint files (always applied)
- `docs/archive/` - Historical documentation for reference


## Services (services/api/)

```
services/api/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py            # Alembic configuration
├── app/                  # FastAPI application
│   ├── agent/            # LangGraph agents
│   │   ├── graph.py      # StateGraph definition
│   │   ├── nodes.py      # Agent nodes (retrieve, rerank, generate)
│   │   └── state.py      # AgentState TypedDict
│   ├── core/             # Core utilities
│   │   ├── embedder.py   # Embedding model wrapper
│   │   ├── minio_client.py
│   │   ├── redis_client.py
│   │   └── security.py   # JWT and password hashing
│   ├── crons/            # Scheduled tasks
│   │   ├── morning_brief.py
│   │   └── system_monitor.py
│   ├── db/               # Database layer
│   │   ├── models.py     # SQLAlchemy ORM models
│   │   ├── repositories.py
│   │   ├── session.py    # Async engine and session
│   │   └── qdrant_client.py
│   ├── routers/          # API endpoints
│   │   ├── auth.py       # Authentication
│   │   ├── chat.py       # Chat with SSE streaming
│   │   ├── conversations.py
│   │   ├── documents.py  # Document upload/management
│   │   ├── health.py     # Health checks
│   │   └── search.py     # Knowledge search
│   ├── services/         # Business logic
│   │   ├── chunker.py    # Document chunking
│   │   ├── embedder.py   # Batch embedding
│   │   ├── indexer.py    # Qdrant indexing
│   │   ├── parser.py     # PDF/DOCX parsing
│   │   ├── reranker.py   # Cross-encoder reranking
│   │   └── search.py     # Hybrid search
│   ├── config.py         # Pydantic Settings
│   ├── dependencies.py   # FastAPI dependencies
│   └── main.py           # FastAPI app factory
├── tests/                # Test suite
│   ├── conftest.py       # Pytest fixtures
│   └── test_*.py         # Test files
├── Dockerfile            # Docker image definition
├── pyproject.toml        # Python dependencies
└── verify_db.py          # Database verification script
```

**Purpose**: FastAPI backend service handling all API requests, RAG pipeline, and business logic.

**Key Components**:
- **Routers**: API endpoints organized by domain
- **Agent**: LangGraph-based RAG agent
- **Services**: Business logic layer
- **DB**: Database models and repositories
- **Core**: Shared utilities and clients


## Applications (apps/web/)

```
apps/web/
├── public/               # Static assets
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── (app)/        # Authenticated routes
│   │   │   ├── admin/
│   │   │   ├── agents/
│   │   │   ├── approvals/
│   │   │   ├── chat/
│   │   │   ├── dashboard/
│   │   │   ├── documents/
│   │   │   ├── finance/
│   │   │   ├── projects/
│   │   │   ├── search/
│   │   │   └── layout.tsx  # Auth guard + Sidebar
│   │   ├── (auth)/       # Public routes
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── favicon.ico
│   │   ├── globals.css   # Dark theme CSS variables
│   │   ├── layout.tsx    # Root layout
│   │   └── page.tsx      # Landing page
│   ├── components/       # React components
│   │   ├── dashboard/    # Dashboard widgets
│   │   ├── layout/       # Layout components
│   │   ├── shared/       # Shared components
│   │   └── ui/           # shadcn/ui components
│   ├── hooks/            # Custom React hooks
│   │   └── useChat.ts    # SSE streaming hook
│   ├── lib/              # Utilities
│   │   ├── api.ts        # Typed API client
│   │   └── utils.ts      # Helper functions
│   ├── store/            # State management
│   │   └── chatStore.ts  # Zustand store
│   └── types/            # TypeScript types
│       └── api.ts        # API response types
├── .env.example          # Environment variable template
├── .env.local            # Local environment variables
├── components.json       # shadcn/ui configuration
├── Dockerfile            # Docker image definition
├── next.config.ts        # Next.js configuration
├── package.json          # Dependencies
├── postcss.config.mjs    # PostCSS configuration
├── tailwind.config.ts    # Tailwind CSS configuration
└── tsconfig.json         # TypeScript configuration
```

**Purpose**: Next.js 15 frontend application with dark theme UI.

**Key Features**:
- App Router with route groups for auth/app separation
- Server-side rendering and client components
- shadcn/ui component library
- Zustand for state management
- SSE streaming for chat


## Infrastructure (infrastructure/docker/)

```
infrastructure/docker/
├── docker-compose.yml    # Service orchestration
├── .env                  # Environment variables (gitignored)
├── .env.example          # Environment variable template
├── init.sql              # PostgreSQL initialization
└── litellm_config.yaml   # LiteLLM configuration (Stage 2+)
```

**Purpose**: Docker Compose configuration for all services.

**Services by Stage**:
- **Stage 1 (6 services)**: postgres, redis, minio, qdrant, co-op-api, co-op-web
- **Stage 2 (+2 services)**: ollama, litellm
- **Stage 3 (+4 services)**: browserless, vault, llm-guard, communication
- **Stage 4 (add as needed)**: temporal, keycloak, traefik, etc.

**Key Files**:
- `docker-compose.yml` - Service definitions with health checks
- `.env.example` - Template with all required variables
- `init.sql` - Database initialization script

## CLI (cli/)

```
cli/
├── coop/                 # CLI package
│   ├── commands/         # Command modules
│   │   ├── approve.py    # Approval management
│   │   ├── backup.py     # Backup operations
│   │   ├── doctor.py     # System diagnostics
│   │   ├── gateway.py    # Service management
│   │   ├── onboard.py    # Onboarding wizard
│   │   └── test.py       # Testing utilities
│   ├── main.py           # CLI entry point
│   └── __init__.py
├── tests/                # CLI tests
├── pyproject.toml        # Python dependencies
└── README.md             # CLI documentation
```

**Purpose**: Command-line interface for managing Co-Op OS.

**Key Commands**:
- `coop gateway up` - Start all services
- `coop gateway down` - Stop all services
- `coop doctor` - Run system diagnostics
- `coop backup` - Backup data


## Scripts (scripts/)

```
scripts/
├── check-consistency.sh  # Configuration consistency checks (future)
├── check-docs.sh         # Documentation validation (future)
├── performance-test.sh   # Performance baseline testing (future)
├── security-scan.sh      # Security scanning (future)
├── validate-mdc.sh       # MDC file validation
└── verify-architecture.py # Architecture verification (future)
```

**Purpose**: Utility scripts for validation, testing, and verification.

## Development Workflow

### Getting Started

1. **Read the steering files** (`.kiro/steering/`)
   - `architecture.md` - Understand the 10-layer architecture
   - `project.md` - Check current phase status
   - `constraints.md` - Learn the hard rules

2. **Check current phase documentation** (`docs/stages/phase-0/`)
   - `INSTALL.md` - Installation instructions
   - `DEVELOPMENT.md` - Development setup
   - `TASKS.md` - Current task list
   - `stage1_implementation.md` - Implementation guide

3. **Review specs** (`.kiro/specs/`)
   - Check active specs for features in development
   - Review requirements, design, and tasks

### Finding Specific Information

| What You Need | Where to Look |
|---------------|---------------|
| Architecture overview | `.kiro/steering/architecture.md` |
| Current phase status | `.kiro/steering/project.md` |
| Development constraints | `.kiro/steering/constraints.md` |
| API endpoints | `docs/rules/co-op-api-contracts.mdc` |
| Coding standards | `docs/rules/co-op-coding-standards.mdc` |
| File structure | `docs/rules/co-op-file-structure.mdc` |
| Installation guide | `docs/stages/phase-0/INSTALL.md` |
| Development setup | `docs/stages/phase-0/DEVELOPMENT.md` |
| Current tasks | `docs/stages/phase-0/TASKS.md` |
| Feature specs | `.kiro/specs/` |
| Historical docs | `docs/archive/` |

### Working on Features

1. **Check if a spec exists** in `.kiro/specs/`
2. **If no spec**, create one using Kiro's spec workflow
3. **Follow the spec** - requirements → design → tasks
4. **Update documentation** as you implement
5. **Run validation scripts** before committing

### Running the System

```bash
# Start all services
cd infrastructure/docker
docker compose up -d

# Check service health
docker compose ps
curl http://localhost:8000/health

# View logs
docker compose logs -f co-op-api

# Stop all services
docker compose down
```

### Testing

```bash
# Backend tests
cd services/api
pytest

# Frontend build
cd apps/web
pnpm build

# Linting
cd services/api && ruff check .
cd apps/web && pnpm lint
```

## Key Principles

1. **Phase Discipline**: Only use services from current phase (Phase 0 = 6 services)
2. **Documentation as Code**: Keep docs in sync with implementation
3. **Spec-Driven Development**: Use `.kiro/specs/` for feature planning
4. **Incremental Growth**: Complete current phase before starting next
5. **Validation First**: Run validation scripts before committing

## Related Documentation

- [Architecture Overview](.kiro/steering/architecture.md)
- [Project Status](.kiro/steering/project.md)
- [Development Constraints](.kiro/steering/constraints.md)
- [Stage Documentation](docs/stages/README.md)
- [Installation Guide](docs/stages/phase-0/INSTALL.md)
- [Development Guide](docs/stages/phase-0/DEVELOPMENT.md)

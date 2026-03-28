# Co-Op System Architecture

This document provides a comprehensive overview of the Co-Op system architecture, including the 10-layer design, component interactions, and data flows.

## Table of Contents

- [Overview](#overview)
- [10-Layer Architecture](#10-layer-architecture)
- [Component Interactions](#component-interactions)
- [Data Flow Patterns](#data-flow-patterns)
- [Technology Stack](#technology-stack)
- [Scalability Considerations](#scalability-considerations)

## Overview

Co-Op is built on a 10-layer architecture that separates concerns and enables independent scaling of different system components. Each layer has specific responsibilities and communicates through well-defined interfaces.

### Design Principles

- **Separation of Concerns** - Each layer handles a specific aspect of the system
- **Loose Coupling** - Layers communicate through interfaces, not direct dependencies
- **Scalability** - Each layer can scale independently based on load
- **Maintainability** - Clear boundaries make the system easier to understand and modify
- **Testability** - Isolated layers enable comprehensive unit and integration testing

## 10-Layer Architecture

### Complete System Diagram

```mermaid
graph TB
    subgraph "Layer 0: Hardware Detection"
        HW[Hardware Detector]
        HW -->|Detects| CPU[CPU Cores]
        HW -->|Detects| RAM[RAM GB]
        HW -->|Detects| GPU[GPU Available]
        HW -->|Assigns| TIER[Tier: SOLO/TEAM/AGENCY]
    end
    
    subgraph "Layer 1: Gateway Dashboard"
        UI[Next.js 16 Frontend]
        UI -->|SSE| STREAM[Real-time Streaming]
        UI -->|Display| DASH[Dashboard]
        UI -->|Display| INBOX[Approval Inbox]
        UI -->|Display| COST[Cost Tracker]
    end
    
    subgraph "Layer 2: Communication Hub"
        COMM[FastAPI Communication]
        COMM -->|Adapter| TG[Telegram Bot]
        COMM -->|Adapter| DC[Discord Bot]
        COMM -->|Adapter| WA[WhatsApp]
        COMM -->|Adapter| EM[Email SMTP]
    end
    
    subgraph "Layer 3: API Gateway & Security"
        GW[Traefik Gateway]
        GW -->|TLS| SEC1[TLS Termination]
        GW -->|Rate Limit| SEC2[Rate Limiting]
        GW -->|Guard| SEC3[LLM Guard]
        GW -->|Secrets| SEC4[Vault]
    end
    
    subgraph "Layer 4: Company Brain"
        BRAIN[Strategic Planner]
        BRAIN -->|Stores| PROFILE[Business Profile]
        BRAIN -->|Generates| PLANS[Weekly Plans]
        BRAIN -->|Research| IMPROVE[Improvements]
        BRAIN -->|Creates| FACTORY[Agent Factory]
    end
    
    subgraph "Layer 5: Agent Workforce"
        AGENTS[LangGraph Agents]
        AGENTS -->|Scout| A1[Lead Scout]
        AGENTS -->|Write| A2[Proposal Writer]
        AGENTS -->|Communicate| A3[Client Comm]
        AGENTS -->|Code| A4[Developer Agent]
        AGENTS -->|Track| A5[Project Tracker]
        AGENTS -->|Invoice| A6[Finance Manager]
        AGENTS -->|Review| A7[Quality Reviewer]
        AGENTS -->|Monitor| A8[System Monitor]
    end
    
    subgraph "Layer 6: Workflow Engine"
        WF[Task Engine]
        WF -->|Queue| ARQ[ARQ Redis Queue]
        WF -->|Durable| CELERY[Celery/Temporal]
        WF -->|Schedule| CRON[Cron Scheduler]
        WF -->|Test| SHADOW[Shadow Environment]
    end
    
    subgraph "Layer 7: Tool Layer"
        TOOLS[Tool Router]
        TOOLS -->|Web| T1[Browserless]
        TOOLS -->|Integrate| T2[Composio MCP]
        TOOLS -->|Execute| T3[Micro-sandbox]
        TOOLS -->|Git| T4[GitHub API]
    end
    
    subgraph "Layer 8: Knowledge & Memory"
        MEM[Memory System]
        MEM -->|Hot| M1[Redis Cache]
        MEM -->|Warm| M2[PostgreSQL]
        MEM -->|Cold| M3[Graphiti+Neo4j]
        MEM -->|Vector| M4[Qdrant]
        MEM -->|Files| M5[MinIO S3]
    end
    
    subgraph "Layer 9: Inference Engine"
        LLM[LiteLLM Router]
        LLM -->|Simple| L1[Llama 3.2 3B]
        LLM -->|Standard| L2[Llama 3.1 8B]
        LLM -->|Complex| L3[Groq/Gemini API]
        LLM -->|Budget| L4[Token Limits]
    end
    
    TIER --> UI
    UI --> COMM
    COMM --> GW
    GW --> BRAIN
    BRAIN --> AGENTS
    AGENTS --> WF
    WF --> TOOLS
    TOOLS --> MEM
    MEM --> LLM
    LLM --> AGENTS
    
    style HW fill:#e1f5ff
    style UI fill:#e8f5e9
    style COMM fill:#fff3e0
    style GW fill:#fce4ec
    style BRAIN fill:#f3e5f5
    style AGENTS fill:#e0f2f1
    style WF fill:#fff9c4
    style TOOLS fill:#ffe0b2
    style MEM fill:#f1f8e9
    style LLM fill:#e3f2fd
```

### Layer 0: Hardware Detection

**Purpose:** Automatically detect system capabilities and assign appropriate tier.

**Components:**
- CPU core detection
- RAM capacity detection
- GPU availability check
- KVM virtualization support

**Tier Assignment:**
- **SOLO** (4GB RAM, 2 cores) - Single developer, local LLMs only
- **TEAM** (8GB RAM, 4 cores) - Small team, hybrid local/cloud LLMs
- **AGENCY** (16GB+ RAM, 8+ cores) - Full agency, all features enabled

### Layer 1: Gateway Dashboard

**Purpose:** Provide user interface for monitoring and control.

**Components:**
- Next.js 16 App Router with React 19
- Server-Sent Events (SSE) for real-time updates
- Dashboard with system health indicators
- Approval inbox for human-in-the-loop decisions
- Cost tracker for budget monitoring

**Key Features:**
- Dark theme UI with Tailwind CSS 4
- Real-time chat streaming
- Document management interface
- Agent activity monitoring

### Layer 2: Communication Hub

**Purpose:** Unified communication interface across multiple channels.

**Components:**
- Telegram Bot with slash commands
- Discord Bot integration
- WhatsApp Business API adapter
- Email (SMTP) notifications

**Communication Patterns:**
- Async message handling
- Real-time thinking display
- Approval request notifications
- Status update broadcasts

### Layer 3: API Gateway & Security

**Purpose:** Secure entry point with authentication, rate limiting, and threat protection.

**Components:**
- Traefik reverse proxy
- TLS termination
- Rate limiting
- LLM Guard for prompt injection detection
- HashiCorp Vault for secrets management

**Security Features:**
- JWT authentication
- Role-based access control (RBAC)
- API key management
- Request validation

### Layer 4: Company Brain

**Purpose:** Strategic planning and business intelligence.

**Components:**
- Business profile storage
- Weekly plan generator
- Research agent for continuous improvement
- Agent factory for dynamic agent creation

**Capabilities:**
- Goal tracking and KPI monitoring
- Win/loss pattern analysis
- Strategy optimization
- Agent configuration management

### Layer 5: Agent Workforce

**Purpose:** Autonomous agents for business operations.

**Agents:**
- **Lead Scout** - Job discovery and scoring
- **Proposal Writer** - Personalized proposal generation
- **Client Communicator** - Professional client interactions
- **Developer Agent** - Code generation and testing
- **Project Tracker** - Milestone and deadline management
- **Finance Manager** - Invoicing and payment tracking
- **Quality Reviewer** - Output validation
- **System Monitor** - Health checks and self-healing

**Agent Framework:**
- LangGraph state machines
- Human-in-the-loop approval workflow
- Self-review and quality checks
- Error handling and retry logic

### Layer 6: Workflow Engine

**Purpose:** Task orchestration and scheduling.

**Components:**
- ARQ (async Redis queue) for short tasks
- Celery/Temporal for durable workflows
- Cron scheduler for periodic tasks
- Shadow environment for safe testing

**Workflow Types:**
- Short parallel tasks (document indexing)
- Long-running workflows (proposal generation)
- Scheduled tasks (lead scouting, backups)
- Test workflows (shadow mode)

### Layer 7: Tool Layer

**Purpose:** External integrations and tool execution.

**Tools:**
- **Browserless** - Headless Chrome for web automation
- **Composio MCP** - 500+ API integrations
- **Micro-sandbox** - Isolated code execution
- **GitHub API** - Repository operations

**Tool Router:**
- Dynamic tool selection
- Error handling and retries
- Result validation
- Usage tracking

### Layer 8: Knowledge & Memory

**Purpose:** Multi-tier data storage and retrieval.

**Storage Tiers:**
- **Hot (Redis)** - Session context, real-time data (< 1ms latency)
- **Warm (PostgreSQL)** - Clients, proposals, results (< 10ms latency)
- **Cold (Graphiti + Neo4j)** - Relationship patterns (< 100ms latency)
- **Knowledge (Qdrant)** - Portfolio, templates (vector search)
- **Documents (MinIO)** - Files, deliverables (S3-compatible)

**Data Flow:**
- Write-through caching
- Lazy loading from cold storage
- Vector similarity search
- Full-text search

### Layer 9: Inference Engine

**Purpose:** LLM routing and budget management.

**LLM Router (LiteLLM):**
- **Simple tasks** → Llama 3.2 3B (local, fast, cheap)
- **Standard tasks** → Llama 3.1 8B (local, balanced)
- **Complex tasks** → Groq/Gemini API (cloud, powerful)

**Budget Enforcement:**
- Per-agent token limits
- Daily budget caps
- Cost tracking and alerts
- Automatic fallback to cheaper models

## Component Interactions

### Service Communication Diagram

```mermaid
graph LR
    subgraph "Frontend"
        WEB[Next.js App]
    end
    
    subgraph "Backend Services"
        API[FastAPI API]
        WORKER[ARQ Worker]
        CRON[Cron Jobs]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL)]
        RD[(Redis)]
        QD[(Qdrant)]
        MO[(MinIO)]
    end
    
    subgraph "External Services"
        OL[Ollama]
        LL[LiteLLM]
    end
    
    WEB -->|HTTP/SSE| API
    API -->|SQL| PG
    API -->|Cache| RD
    API -->|Vector Search| QD
    API -->|File Storage| MO
    API -->|Enqueue| RD
    RD -->|Dequeue| WORKER
    WORKER -->|SQL| PG
    WORKER -->|Vector| QD
    WORKER -->|Files| MO
    CRON -->|Monitor| API
    CRON -->|Backup| PG
    CRON -->|Backup| QD
    CRON -->|Backup| MO
    API -->|Inference| OL
    API -->|Gateway| LL
    LL -->|Local| OL
    
    style WEB fill:#4CAF50
    style API fill:#2196F3
    style WORKER fill:#FF9800
    style CRON fill:#9C27B0
    style PG fill:#336791
    style RD fill:#DC382D
    style QD fill:#00BCD4
    style MO fill:#E91E63
    style OL fill:#FFC107
    style LL fill:#795548
```

### Agent Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Researching: New Task
    Researching --> Planning: Context Retrieved
    Planning --> Executing: Plan Created
    Executing --> Reviewing: Action Complete
    Reviewing --> Executing: Needs Revision
    Reviewing --> AwaitingApproval: Quality Check Passed
    AwaitingApproval --> Executing: Approved
    AwaitingApproval --> Idle: Rejected
    Executing --> Failed: Error
    Failed --> Idle: Max Retries
    Failed --> Researching: Retry
    AwaitingApproval --> Completed: Final Approval
    Completed --> [*]
    
    note right of Researching
        Retrieve relevant context
        from Qdrant and PostgreSQL
    end note
    
    note right of Planning
        Generate action plan
        using LLM
    end note
    
    note right of Executing
        Execute tools and
        external APIs
    end note
    
    note right of Reviewing
        Self-review output
        for quality
    end note
    
    note right of AwaitingApproval
        Human-in-the-loop
        approval required
    end note
```

## Data Flow Patterns

### RAG Pipeline Flow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant MinIO
    participant Parser
    participant Chunker
    participant Embedder
    participant Qdrant
    participant Search
    
    User->>API: Upload Document
    API->>MinIO: Store File
    MinIO-->>API: File URL
    API->>Parser: Parse Content
    Parser-->>API: Extracted Text
    API->>Chunker: Split Text
    Chunker-->>API: Text Chunks
    API->>Embedder: Generate Embeddings
    Embedder-->>API: Vector Embeddings
    API->>Qdrant: Index Vectors
    Qdrant-->>API: Indexed
    API-->>User: Status: READY
    
    Note over User,Search: Search Phase
    
    User->>API: Search Query
    API->>Embedder: Embed Query
    Embedder-->>API: Query Vector
    API->>Search: Hybrid Search
    Search->>Qdrant: Vector Search
    Qdrant-->>Search: Top Results
    Search-->>API: Ranked Results
    API-->>User: Search Results
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant DB as PostgreSQL
    participant Redis
    
    Client->>API: POST /auth/token
    Note over Client,API: username + password
    API->>DB: Verify Credentials
    DB-->>API: User Data
    API->>API: Generate JWT
    API->>Redis: Store Session
    API-->>Client: Access Token + Refresh Token
    
    Note over Client,API: Protected Request
    
    Client->>API: GET /api/resource
    Note over Client,API: Authorization: Bearer {token}
    API->>API: Verify JWT
    API->>Redis: Check Session
    Redis-->>API: Session Valid
    API-->>Client: Protected Resource
    
    Note over Client,API: Token Refresh
    
    Client->>API: POST /auth/refresh
    Note over Client,API: refresh_token
    API->>Redis: Verify Refresh Token
    Redis-->>API: Valid
    API->>API: Generate New JWT
    API-->>Client: New Access Token
```

### Chat Streaming Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Agent as LangGraph Agent
    participant Qdrant
    participant LLM
    
    User->>API: POST /chat/stream
    Note over User,API: message + conversation_id
    API->>Agent: Invoke Agent
    Agent->>Qdrant: Retrieve Context
    Qdrant-->>Agent: Relevant Documents
    Agent->>Agent: Rerank Results
    
    Note over Agent,LLM: Citation Phase
    Agent->>API: SSE: event=citation
    API-->>User: Citation Data
    
    Note over Agent,LLM: Generation Phase
    Agent->>LLM: Generate Response
    loop Token Streaming
        LLM-->>Agent: Token
        Agent->>API: SSE: event=token
        API-->>User: Token Data
    end
    
    Agent->>API: SSE: event=done
    API-->>User: Conversation ID
```

## Technology Stack

### Technology Stack Visualization

```mermaid
graph TB
    subgraph "Frontend Layer"
        NEXTJS[Next.js 16.1.4]
        REACT[React 19.0.0]
        TAILWIND[Tailwind CSS 4.0.0]
        SHADCN[shadcn/ui]
        ZUSTAND[Zustand 5.0.2]
        TANSTACK[TanStack Query v5.62.11]
    end
    
    subgraph "Backend Layer"
        FASTAPI[FastAPI 0.115.12]
        SQLALCHEMY[SQLAlchemy 2.0.36]
        LANGGRAPH[LangGraph 0.2+]
        PYDANTIC[Pydantic 2.10.6]
        ARQ[ARQ 0.26.1]
    end
    
    subgraph "AI/ML Layer"
        ST[sentence-transformers]
        EMBEDDINGS[all-MiniLM-L6-v2]
        LITELLM[LiteLLM 1.55+]
        LANGCHAIN[LangChain 0.3+]
    end
    
    subgraph "Infrastructure Layer"
        POSTGRES[PostgreSQL 16]
        REDIS[Redis 7.4]
        QDRANT[Qdrant 1.12.4]
        MINIO[MinIO RELEASE.2024-06-04]
        DOCKER[Docker Compose V2]
    end
    
    NEXTJS --> FASTAPI
    FASTAPI --> LANGGRAPH
    LANGGRAPH --> ST
    FASTAPI --> POSTGRES
    FASTAPI --> REDIS
    FASTAPI --> QDRANT
    FASTAPI --> MINIO
    FASTAPI --> LITELLM
    
    style NEXTJS fill:#4CAF50
    style FASTAPI fill:#2196F3
    style LANGGRAPH fill:#9C27B0
    style ST fill:#FF9800
    style POSTGRES fill:#336791
    style REDIS fill:#DC382D
    style QDRANT fill:#00BCD4
    style MINIO fill:#E91E63
```

### Component Versions

| Component | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.1.4 | Frontend framework with App Router |
| React | 19.0.0 | UI library with Server Components |
| Tailwind CSS | 4.0.0 | Utility-first CSS framework |
| FastAPI | 0.115.12 | Async Python web framework |
| SQLAlchemy | 2.0.36 | Async ORM for PostgreSQL |
| LangGraph | 0.2+ | Agent state machine framework |
| PostgreSQL | 16 | Primary relational database |
| Redis | 7.4 | Cache and message broker |
| Qdrant | 1.12.4 | Vector database for RAG |
| MinIO | 2024-06-04 | S3-compatible object storage |
| LiteLLM | 1.55+ | Unified LLM gateway |

## Scalability Considerations

### Horizontal Scaling

**Frontend (Next.js):**
- Stateless design enables multiple instances
- Load balancer distributes traffic
- CDN for static assets

**Backend (FastAPI):**
- Multiple API instances behind load balancer
- Shared Redis for session state
- Shared PostgreSQL for data persistence

**Workers (ARQ):**
- Multiple worker instances process queue
- Redis pub/sub for task distribution
- Automatic task retry on failure

### Vertical Scaling

**Database (PostgreSQL):**
- Increase RAM for larger working set
- Add CPU cores for parallel queries
- Use connection pooling (PgBouncer)

**Vector Database (Qdrant):**
- Increase RAM for in-memory index
- Add CPU cores for parallel search
- Use HNSW index for fast similarity search

**Object Storage (MinIO):**
- Add disk space for more documents
- Use erasure coding for redundancy
- Distribute across multiple drives

### Caching Strategy

**Redis Caching:**
- Session data (TTL: 7 days)
- API responses (TTL: 5 minutes)
- Search results (TTL: 1 hour)
- User preferences (TTL: 24 hours)

**Application Caching:**
- LRU cache for embeddings
- Query result cache
- Document metadata cache

### Performance Targets

| Operation | Target Latency | Notes |
|-----------|----------------|-------|
| Document upload | < 1s | Async processing |
| Search query | < 500ms | Hybrid search with reranking |
| Chat response (first token) | < 2s | Including retrieval |
| Chat response (full) | < 10s | Streaming tokens |
| Authentication | < 100ms | JWT validation |
| Health check | < 50ms | All services |

## Related Documentation

- [Main README](../README.md) - Project overview and quick start
- [Backend API Documentation](../services/api/README.md) - API reference
- [Frontend Documentation](../apps/web/README.md) - UI architecture
- [Docker Infrastructure](../infrastructure/docker/README.md) - Deployment guide
- [Database Schema](./DATABASE.md) - Data model
- [Security Guide](./SECURITY.md) - Security best practices

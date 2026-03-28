# Stage 3 — Working Agents
## Implementation Guide

**What this stage delivers:** Agents that find leads, write proposals, submit them to Upwork, communicate with clients, track projects, and create invoices. This is the revenue-generating stage.

**Services (12):** + browserless, vault, llm-guard, communication

**Timeline:** Months 3-4 (8 weeks)

---

## What You Get

### Month 3
- Browserless (headless Chrome) for real web scraping
- HashiCorp Vault for credential management
- LLM Guard for prompt injection protection
- Dedicated communication service (Telegram + Email)
- Proposal Writer agent generating personalized proposals
- HITL approval system with Telegram /approve commands
- Outreach Manager submitting approved proposals

### Month 4
- Client Communicator handling email replies
- Project Tracker with milestone alerts
- Finance Manager creating invoices
- Simulation mode for safe testing
- Research Agent scanning GitHub/HuggingFace
- Docker sandbox for code execution
- Client portal (read-only status page)

---

## Key Architectural Decisions

### STILL No Temporal — Use ARQ Workflows

The proposal pipeline (find → write → approve → submit → follow-up) runs as a chain of ARQ tasks. Each step completes independently and queues the next:

```python
# Simplified flow using ARQ task chaining
async def proposal_pipeline(ctx, job_id: str):
    proposal = await write_proposal(job_id)
    approval_id = await queue_for_approval(proposal)
    # Pipeline pauses here — human approves via Telegram or dashboard
    # When approved, outreach_task is enqueued automatically
```

This works until you have workflows that span multiple days and need crash recovery. That's when you add Temporal (Stage 4).

### STILL No Neo4j — Use PostgreSQL JSONB

```sql
CREATE TABLE client_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    facts JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- "What tone does this client prefer?"
SELECT facts->>'preferred_tone' FROM client_memory WHERE client_id = $1;
```

Switch to Neo4j when you have 50+ clients and need relationship queries like "which proposal style works best with UK fintech companies?"

### STILL No OPA — Use FastAPI Role Checks

```python
@require_role([Role.ADMIN, Role.MANAGER])
async def approve_action(id: str, current_user: User = Depends()):
    ...
```

Add OPA in Stage 4 when you have 5+ role types and complex policy rules.

### Why Add Vault Now?

You're about to store Upwork credentials, email tokens, OAuth keys, and API keys. Having 12 services reading from a single .env file is fragile and insecure. Vault encrypts secrets and gives each service a scoped token.

### Why Add LLM Guard Now?

Agents will receive external content (job descriptions, client messages). A malicious job description could try to hijack your agent. LLM Guard scans inputs before they reach the LLM.

---

## Implementation Steps

### Month 3: Infrastructure + Proposal Pipeline

```bash
# Week 1: Add 4 new services
# docker-compose.yml additions:
#   browserless: browserless/chrome:latest, port 8030
#   vault: hashicorp/vault:latest, port 8200
#   llm-guard: laiyer/llm-guard:latest, port 8060
#   communication: custom FastAPI, port 8010

# Week 2: Communication Service
# Create services/communication/ with Telegram + Email adapters
# Move Telegram bot from co-op-api to communication service

# Week 3: Proposal Writer + HITL
# Build Proposal Writer with portfolio RAG
# Build HITL approval system
# Connect Composio MCP for Upwork API

# Week 4: Outreach Manager
# Submit approved proposals via Composio
# Set up prompt versioning
```

### Month 4: Revenue Operations

```bash
# Week 1: Client Communication
# Build Client Communicator agent
# Build Project Tracker agent
# Build Finance Manager agent

# Week 2: Polish
# Build Simulation Mode
# Build client portal
# Set up prompt quality CI

# Week 3: Research + Testing
# Build Research Agent v1
# Build Docker sandbox
# Full end-to-end revenue test

# Week 4: Optional code delivery
# (only if delivering websites/apps to clients)
```

---

## The Proposal Pipeline (End-to-End)

```
Lead Scout (every 4h)
    ↓ finds jobs matching your profile
Proposal Writer
    ↓ drafts personalized proposal (RAG on portfolio)
    ↓ self-reviews (specific? references job? under 200 words?)
HITL Queue
    ↓ you see: "3 proposals ready — /approve 1 2 3"
    ↓ you approve (Telegram or dashboard)
Outreach Manager
    ↓ submits to Upwork via Composio
    ↓ sets 3-day follow-up reminder
Client Communicator
    ↓ handles client replies
    ↓ escalates complex items (price negotiations, complaints)
Project Tracker
    ↓ creates milestones, sends deadline alerts
Finance Manager
    ↓ creates invoices, sends 7-day payment reminders
```

---

## How to Verify Stage 3 Is Complete

| Check | Command / Action | Expected Result |
|-------|-----------------|-----------------|
| Browserless | Playwright → ws://localhost:8030 | Page fetched |
| Vault | All secrets in Vault, .env clean | No secrets in .env |
| LLM Guard | Send injection attempt | Returns 400 |
| Communication service | Telegram + email | Both work |
| Proposal Writer | Real job → proposal | Personalized draft |
| HITL | /approve 1 in Telegram | Proposal submitted |
| Simulation mode | Toggle to Simulation | Fake jobs, no real sends |
| Client portal | Visit portal URL | Status page loads |
| E2E revenue flow | Full pipeline test | Real proposal submitted |
| GitHub tag | Check Tags | v0.4.0 visible |

---

## Common Pitfalls

1. **Vault initialization** — Run `vault operator init` and `vault operator unseal` on first start. Store the unseal keys securely.
2. **Composio OAuth refresh** — Tokens expire. Composio handles refresh, but verify it works after 24 hours.
3. **LLM Guard false positives** — Tune sensitivity. Job descriptions may contain words that trigger toxicity filters.
4. **Browserless memory** — Limit `MAX_CONCURRENT_SESSIONS=2` to avoid OOM on 8GB machines.
5. **Email deliverability** — Use a proper SMTP provider (SendGrid, Mailgun) to avoid spam folders.

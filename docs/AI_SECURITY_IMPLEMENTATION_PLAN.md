# AI Security Implementation Plan for Co-Op

**Date:** 2027-01-28  
**Version:** 1.0  
**Target:** Phase 1.5 (Post v1.0.3, Pre Phase 2)

## Executive Summary

This document outlines a comprehensive AI security implementation plan for Co-Op, a self-hosted, open-source Enterprise AI Operating System. The plan addresses the unique security challenges of autonomous AI agents while maintaining the project's core principles: self-hosted, no cloud dependencies, and Apache 2.0 licensed.

## Table of Contents

1. [Project Analysis & Security Requirements](#project-analysis)
2. [Questions & Clarifications](#questions)
3. [Security Architecture](#security-architecture)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Task List](#task-list)
6. [Best Practices Research](#best-practices)
7. [Testing Strategy](#testing-strategy)

---

## Project Analysis & Security Requirements {#project-analysis}

### Current State (v1.0.3)

**What's Working:**
- Full RAG pipeline with hybrid search
- LangGraph research agent (read-only)
- JWT authentication
- SSE streaming chat
- Docker-based deployment
- All services self-hosted

**Security Gaps Identified:**

1. **No prompt injection protection** - User inputs go directly to LLM
2. **No tool permission system** - Agents can theoretically call any tool
3. **No sandboxed execution** - Tools run in main process
4. **No model allowlist** - Any model can be used via LiteLLM
5. **No rate limiting** - Token cost explosion risk
6. **No data redaction** - Secrets could leak in logs/responses
7. **No agent RBAC** - All agents have same permissions
8. **No audit logging** - Security events not tracked

### Unique Requirements for Self-Hosted AI Platform

1. **No External Dependencies** - All security must run locally
2. **Open Source** - Security code must be auditable
3. **Multi-Agent Architecture** - 8 agents planned (Phase 2+)
4. **HITL Integration** - Security must work with existing approval system
5. **Docker-Based** - Sandboxing must use containers
6. **LangGraph Integration** - Security hooks at graph nodes
7. **Performance** - Security checks must not slow down responses
8. **User Privacy** - All data stays on user's infrastructure

---

## Questions & Clarifications {#questions}

### Critical Questions

1. **Agent Capabilities**
   - Q: Which tools should each agent type be allowed to use?
   - Current: Only Research Agent exists (read-only)
   - Future: 7 more agents with varying permissions
   - Decision Needed: Define tool permission matrix

2. **Sandboxing Strategy**
   - Q: Which tools need sandboxing?
   - Options: Python code execution, shell commands, file operations
   - Current: No code execution tools exist yet
   - Decision: Implement sandbox infrastructure now for Phase 2

3. **Model Control**
   - Q: Should users be able to add custom models?
   - Current: LiteLLM supports any model
   - Security: Allowlist prevents unauthorized models
   - Decision: Configurable allowlist in settings

4. **Rate Limiting Scope**
   - Q: Limit by user, tenant, or agent?
   - Current: Multi-tenant architecture exists
   - Decision: Per-user limits with tenant overrides

5. **Prompt Injection Severity**
   - Q: Block or warn on detection?
   - Options: Hard block vs. log + continue
   - Decision: Block by default, configurable per tenant

6. **Audit Retention**
   - Q: How long to keep security audit logs?
   - Current: audit_events table exists
   - Decision: 90 days default, configurable

### Implementation Questions

7. **Performance Impact**
   - Q: What's acceptable latency for security checks?
   - Target: <50ms for prompt guard, <10ms for tool guard
   - Approach: In-memory pattern matching, no external calls

8. **Backward Compatibility**
   - Q: Must existing APIs remain unchanged?
   - Decision: Yes, security is transparent middleware

9. **Configuration Management**
   - Q: Where to store security policies?
   - Options: Database, config files, environment variables
   - Decision: Database for runtime, env for deployment

10. **Testing Requirements**
    - Q: How to test security without real attacks?
    - Approach: Synthetic attack dataset, property-based tests

---

## Security Architecture {#security-architecture}

### Defense-in-Depth Layers

```
User Input
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 1: Input Validation          │
│  - Prompt injection detection       │
│  - Input sanitization               │
│  - Size limits                      │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 2: Authentication & RBAC     │
│  - JWT validation (existing)        │
│  - User role check                  │
│  - Tenant isolation                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 3: LLM Gateway               │
│  - Model allowlist                  │
│  - Rate limiting                    │
│  - Token tracking                   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 4: Agent Controller          │
│  - Agent RBAC                       │
│  - Tool permission check            │
│  - HITL integration                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 5: Tool Execution            │
│  - Sandboxed execution              │
│  - Resource limits                  │
│  - Network isolation                │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 6: Output Filtering          │
│  - Secret redaction                 │
│  - PII filtering                    │
│  - Response validation              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Layer 7: Audit & Monitoring        │
│  - Security event logging           │
│  - Anomaly detection                │
│  - Alert generation                 │
└─────────────────────────────────────┘
    │
    ▼
Response to User
```

### Component Architecture

```
services/api/app/
├── security/                    # NEW: Security module
│   ├── __init__.py
│   ├── prompt_guard.py         # Layer 1: Prompt injection detection
│   ├── tool_guard.py           # Layer 4: Tool permission system
│   ├── data_guard.py           # Layer 6: Secret redaction
│   ├── rate_limiter.py         # Layer 3: Rate limiting
│   ├── audit_logger.py         # Layer 7: Security audit
│   └── sandbox/                # Layer 5: Sandboxed execution
│       ├── __init__.py
│       ├── docker_sandbox.py   # Docker-based sandbox
│       └── resource_limits.py  # CPU/memory limits
│
├── services/
│   └── llm_gateway.py          # MODIFIED: Add model allowlist
│
├── middleware/
│   └── security_middleware.py  # NEW: FastAPI middleware
│
└── agent/
    ├── graph.py                # MODIFIED: Add security hooks
    └── permissions.py          # NEW: Agent RBAC definitions
```

---


## Implementation Roadmap {#implementation-roadmap}

### Phase 1.5: Core Security (2-3 weeks)

**Goal:** Implement essential AI security layers before Phase 2 agents

#### Week 1: Foundation
- [ ] Create security module structure
- [ ] Implement prompt injection guard
- [ ] Add LLM gateway with model allowlist
- [ ] Implement rate limiting
- [ ] Add security middleware

#### Week 2: Agent Security
- [ ] Implement tool permission system
- [ ] Add agent RBAC definitions
- [ ] Integrate with LangGraph nodes
- [ ] Create audit logging system

#### Week 3: Advanced Protection
- [ ] Implement data redaction
- [ ] Create Docker sandbox infrastructure
- [ ] Add security configuration UI
- [ ] Write comprehensive tests

### Phase 2: Agent Expansion (Parallel with agent development)

**Goal:** Secure new agents as they're developed

- [ ] Define permissions for each new agent
- [ ] Sandbox tools that execute code
- [ ] Implement agent-specific rate limits
- [ ] Add anomaly detection

### Phase 3: Enterprise Features (Future)

**Goal:** Advanced security for enterprise deployments

- [ ] Policy-based access control (OPA integration)
- [ ] Advanced threat detection
- [ ] Security dashboard
- [ ] Compliance reporting (SOC 2, ISO 27001)

---

## Task List {#task-list}

### Task 1: Create Security Module Structure

**Priority:** HIGH  
**Effort:** 2 hours  
**Dependencies:** None

**Subtasks:**
1.1. Create `services/api/app/security/` directory
1.2. Create `__init__.py` with module exports
1.3. Add security dependencies to `pyproject.toml`
1.4. Create base exception classes

**Files to Create:**
- `services/api/app/security/__init__.py`
- `services/api/app/security/exceptions.py`

**Dependencies to Add:**
```toml
# Security
"slowapi>=0.1.9",           # Already exists
"python-multipart>=0.0.9",  # Already exists
```

---

### Task 2: Implement Prompt Injection Guard

**Priority:** HIGH  
**Effort:** 4 hours  
**Dependencies:** Task 1

**Research Findings:**
- 73% of production AI deployments have prompt injection vulnerabilities (OWASP 2024)
- Multi-agent NLP frameworks show 94% detection accuracy
- Token-level sanitization more effective than sample-level classification

**Implementation Approach:**
1. Pattern-based detection (fast, low false positives)
2. Embedding-based classification (high accuracy, slower)
3. Hybrid approach: patterns first, then ML if suspicious

**Subtasks:**
2.1. Create `prompt_guard.py` with pattern matching
2.2. Add configurable blocked patterns
2.3. Implement severity levels (block vs. warn)
2.4. Add bypass mechanism for admin users
2.5. Create unit tests with attack samples

**Files to Create:**
- `services/api/app/security/prompt_guard.py`
- `services/api/tests/security/test_prompt_guard.py`

**Configuration:**
```python
# In database: security_policies table
{
  "prompt_injection": {
    "enabled": true,
    "action": "block",  # or "warn"
    "patterns": [
      "ignore previous instructions",
      "reveal system prompt",
      "send api key",
      "exfiltrate",
      "you are now in developer mode"
    ],
    "bypass_roles": ["admin"]
  }
}
```

---

### Task 3: Implement LLM Gateway with Model Allowlist

**Priority:** HIGH  
**Effort:** 3 hours  
**Dependencies:** Task 1

**Research Findings:**
- LiteLLM supports 100+ model providers
- Model allowlist prevents unauthorized model usage
- Token tracking essential for cost control

**Subtasks:**
3.1. Create `llm_gateway.py` wrapper around LiteLLM
3.2. Implement model allowlist validation
3.3. Add token usage tracking
3.4. Implement cost calculation
3.5. Add model-specific rate limits

**Files to Create:**
- `services/api/app/services/llm_gateway.py` (modify existing)
- `services/api/tests/services/test_llm_gateway.py`

**Configuration:**
```python
# In settings
ALLOWED_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "claude-3-5-sonnet",
    "gemini-1.5-pro",
    "ollama/llama3.1:8b",
    "ollama/llama3.2:3b"
]

# In database: model_costs table
{
  "gpt-4o": {
    "input_cost_per_1k": 0.005,
    "output_cost_per_1k": 0.015
  }
}
```

---

### Task 4: Implement Rate Limiting

**Priority:** HIGH  
**Effort:** 3 hours  
**Dependencies:** Task 1

**Research Findings:**
- slowapi already in dependencies
- Redis-backed rate limiting for distributed systems
- Per-user, per-tenant, and per-endpoint limits

**Subtasks:**
4.1. Configure slowapi with Redis backend
4.2. Add rate limit decorators to endpoints
4.3. Implement tenant-level overrides
4.4. Add rate limit headers to responses
4.5. Create rate limit exceeded handler

**Files to Modify:**
- `services/api/main.py` (add slowapi configuration)
- `services/api/app/routers/chat.py` (add rate limits)

**Configuration:**
```python
# Default limits
RATE_LIMITS = {
    "chat": "10/minute",
    "search": "30/minute",
    "documents": "20/minute"
}

# Tenant overrides in database
{
  "tenant_id": "uuid",
  "rate_limits": {
    "chat": "100/minute",  # Enterprise tier
    "search": "300/minute"
  }
}
```

---

### Task 5: Implement Tool Permission System

**Priority:** HIGH  
**Effort:** 5 hours  
**Dependencies:** Task 1

**Research Findings:**
- LangGraph supports tool filtering at graph level
- Cerbos and Auth0 FGA used for agent authorization
- Role-based access control (RBAC) most common pattern

**Subtasks:**
5.1. Define agent roles enum
5.2. Create tool permission matrix
5.3. Implement permission validation
5.4. Integrate with LangGraph tool calls
5.5. Add permission denied logging

**Files to Create:**
- `services/api/app/security/tool_guard.py`
- `services/api/app/agent/permissions.py`
- `services/api/tests/security/test_tool_guard.py`

**Permission Matrix:**
```python
AGENT_PERMISSIONS = {
    AgentRole.RESEARCH: [
        "search_documents",
        "retrieve_context",
        "generate_summary"
    ],
    AgentRole.SUPPORT: [
        "search_documents",
        "send_email",
        "create_ticket"
    ],
    AgentRole.CODE: [
        "read_file",
        "execute_code_sandbox",
        "run_tests"
    ],
    AgentRole.ANALYTICS: [
        "query_database",
        "generate_chart",
        "export_report"
    ],
    AgentRole.COMMUNICATION: [
        "send_email",
        "send_slack",
        "schedule_meeting"
    ],
    AgentRole.HR: [
        "read_employee_data",
        "generate_report",
        "send_notification"
    ]
}
```

---

### Task 6: Implement Data Redaction

**Priority:** MEDIUM  
**Effort:** 3 hours  
**Dependencies:** Task 1

**Research Findings:**
- Regex-based redaction for common secret patterns
- PII detection using NER models (optional, heavier)
- Redact before logging and before LLM output

**Subtasks:**
6.1. Create `data_guard.py` with secret patterns
6.2. Implement redaction function
6.3. Add PII detection (optional)
6.4. Integrate with logging system
6.5. Add redaction to LLM responses

**Files to Create:**
- `services/api/app/security/data_guard.py`
- `services/api/tests/security/test_data_guard.py`

**Secret Patterns:**
```python
SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9]{20,}", "OPENAI_KEY"),
    (r"AIza[0-9A-Za-z_-]{35}", "GOOGLE_API_KEY"),
    (r"AKIA[0-9A-Z]{16}", "AWS_ACCESS_KEY"),
    (r"ghp_[A-Za-z0-9]{36}", "GITHUB_TOKEN"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "SLACK_TOKEN"),
    (r"-----BEGIN.*PRIVATE KEY-----.*?-----END.*PRIVATE KEY-----", "PRIVATE_KEY"),
]
```

---

### Task 7: Implement Docker Sandbox

**Priority:** MEDIUM  
**Effort:** 6 hours  
**Dependencies:** Task 1

**Research Findings:**
- Docker provides strong isolation
- gVisor adds additional security layer
- Resource limits prevent DoS

**Subtasks:**
7.1. Create `sandbox/docker_sandbox.py`
7.2. Implement Python code executor
7.3. Add resource limits (CPU, memory, time)
7.4. Implement network isolation
7.5. Add file system restrictions
7.6. Create sandbox cleanup mechanism

**Files to Create:**
- `services/api/app/security/sandbox/__init__.py`
- `services/api/app/security/sandbox/docker_sandbox.py`
- `services/api/app/security/sandbox/resource_limits.py`
- `services/api/tests/security/test_sandbox.py`

**Sandbox Configuration:**
```python
SANDBOX_LIMITS = {
    "memory": "256m",
    "cpu_quota": 50000,  # 50% of one core
    "timeout": 30,  # seconds
    "network": False,
    "read_only": True,
    "allowed_packages": [
        "numpy", "pandas", "matplotlib"
    ]
}
```

---

### Task 8: Implement Security Audit Logging

**Priority:** MEDIUM  
**Effort:** 4 hours  
**Dependencies:** Task 1

**Subtasks:**
8.1. Create `audit_logger.py`
8.2. Define security event types
8.3. Implement structured logging
8.4. Add audit log rotation
8.5. Create audit log query API

**Files to Create:**
- `services/api/app/security/audit_logger.py`
- `services/api/app/routers/audit.py` (new endpoint)
- `services/api/tests/security/test_audit_logger.py`

**Event Types:**
```python
class SecurityEventType(Enum):
    PROMPT_INJECTION_DETECTED = "prompt_injection_detected"
    TOOL_PERMISSION_DENIED = "tool_permission_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    MODEL_NOT_ALLOWED = "model_not_allowed"
    SANDBOX_VIOLATION = "sandbox_violation"
    SECRET_REDACTED = "secret_redacted"
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHORIZATION_FAILED = "authorization_failed"
```

---

### Task 9: Integrate Security with LangGraph

**Priority:** HIGH  
**Effort:** 4 hours  
**Dependencies:** Tasks 2, 5

**Subtasks:**
9.1. Add security hooks to graph nodes
9.2. Implement pre-tool-call validation
9.3. Add post-tool-call filtering
9.4. Integrate with HITL system
9.5. Add security checkpoints

**Files to Modify:**
- `services/api/app/agent/graph.py`
- `services/api/app/agent/nodes.py`

**Integration Points:**
```python
# In graph.py
from app.security.tool_guard import validate_tool_call
from app.security.prompt_guard import sanitize_prompt

def create_graph():
    graph = StateGraph(AgentState)
    
    # Add security checkpoint before tool execution
    graph.add_node("security_check", security_checkpoint)
    graph.add_node("retrieve", retrieve_node)
    
    graph.add_edge(START, "security_check")
    graph.add_edge("security_check", "retrieve")
    
    return graph

def security_checkpoint(state: AgentState):
    # Validate tool permissions
    # Check rate limits
    # Log security events
    return state
```

---

### Task 10: Create Security Configuration UI

**Priority:** LOW  
**Effort:** 6 hours  
**Dependencies:** Tasks 2-8

**Subtasks:**
10.1. Create security settings page in admin panel
10.2. Add model allowlist management
10.3. Add rate limit configuration
10.4. Add prompt injection pattern editor
10.5. Add security audit log viewer

**Files to Create:**
- `apps/web/src/app/(app)/admin/security/page.tsx`
- `apps/web/src/components/admin/SecuritySettings.tsx`

---


## Best Practices Research {#best-practices}

### 1. Prompt Injection Prevention

**Research Sources:**
- OWASP AI Security (2024): 73% of AI deployments vulnerable
- arXiv 2503.11517: Multi-agent NLP framework for detection
- arXiv 2601.13186: Agentic AI with semantic caching

**Key Findings:**
1. **Layered Detection:** Use both pattern matching and ML models
2. **Token-Level Sanitization:** More effective than sample-level
3. **Semantic Caching:** Cache known attack patterns for fast detection
4. **Multi-Agent Validation:** Use separate agent to validate responses

**Recommended Approach for Co-Op:**
- Start with pattern-based detection (fast, low overhead)
- Add ML-based detection in Phase 2 (higher accuracy)
- Use semantic similarity for attack pattern matching
- Implement surgical token removal instead of full blocking

**Implementation Priority:** HIGH (Task 2)

---

### 2. Tool Sandboxing

**Research Sources:**
- dida.do: Secure Python sandbox for LLM agents
- amirmalik.net: Code sandboxes for AI agents
- arXiv 2504.00018: Securing test environments for untrusted code

**Key Findings:**
1. **Docker Isolation:** Strong security boundary
2. **Resource Limits:** Prevent DoS attacks
3. **Network Isolation:** Block external communication
4. **Read-Only Filesystem:** Prevent persistence
5. **gVisor:** Additional kernel-level isolation

**Recommended Approach for Co-Op:**
- Use Docker for sandbox isolation
- Implement strict resource limits (CPU, memory, time)
- Disable network access by default
- Use read-only filesystem with temp directory
- Add gVisor in Phase 3 for enterprise deployments

**Implementation Priority:** MEDIUM (Task 7)

---

### 3. Agent Authorization

**Research Sources:**
- Cerbos + LangGraph: Authorization for RAG agents
- Auth0 FGA + LangGraph: Fine-grained access control
- LangGraph Platform: Built-in auth system

**Key Findings:**
1. **RBAC:** Role-based access control most common
2. **Policy-Based:** OPA/Cerbos for complex policies
3. **Resource-Level:** Control access to specific data
4. **Tool-Level:** Control which tools agents can use

**Recommended Approach for Co-Op:**
- Start with RBAC (simple, effective)
- Define agent roles and tool permissions
- Integrate with existing JWT auth
- Add policy-based control in Phase 3 (OPA)

**Implementation Priority:** HIGH (Task 5)

---

### 4. Rate Limiting

**Research Sources:**
- slowapi documentation
- Redis-based distributed rate limiting
- Token-based cost control

**Key Findings:**
1. **Multi-Level:** User, tenant, and endpoint limits
2. **Token-Based:** Track LLM token usage
3. **Cost Control:** Prevent runaway costs
4. **Distributed:** Use Redis for multi-instance deployments

**Recommended Approach for Co-Op:**
- Use slowapi with Redis backend
- Implement per-user and per-tenant limits
- Track token usage and costs
- Add configurable limits per plan tier

**Implementation Priority:** HIGH (Task 4)

---

### 5. Secret Management

**Research Sources:**
- OWASP Secret Management
- Regex patterns for common secrets
- PII detection using NER

**Key Findings:**
1. **Regex Patterns:** Fast detection of common secrets
2. **Redaction:** Replace with [REDACTED] placeholder
3. **Logging:** Never log secrets
4. **LLM Responses:** Filter before returning to user

**Recommended Approach for Co-Op:**
- Implement regex-based secret detection
- Redact before logging and before LLM output
- Add PII detection in Phase 2 (optional)
- Use structured logging with automatic redaction

**Implementation Priority:** MEDIUM (Task 6)

---

### 6. LLM Gateway Security

**Research Sources:**
- LiteLLM security best practices
- Model allowlist patterns
- Token tracking and cost control

**Key Findings:**
1. **Model Allowlist:** Prevent unauthorized models
2. **Token Tracking:** Monitor usage and costs
3. **Retry Logic:** Handle failures gracefully
4. **Fallback Models:** Use cheaper models when possible

**Recommended Approach for Co-Op:**
- Implement model allowlist in gateway
- Track token usage per user/tenant
- Calculate costs based on model pricing
- Add model fallback logic

**Implementation Priority:** HIGH (Task 3)

---

### 7. Audit Logging

**Research Sources:**
- OWASP Logging Cheat Sheet
- Structured logging best practices
- Security event taxonomy

**Key Findings:**
1. **Structured Logging:** JSON format for parsing
2. **Event Types:** Define clear taxonomy
3. **Retention:** 90 days minimum for security events
4. **Alerting:** Real-time alerts for critical events

**Recommended Approach for Co-Op:**
- Use structlog (already in dependencies)
- Define security event types
- Store in audit_events table (already exists)
- Add real-time alerting in Phase 2

**Implementation Priority:** MEDIUM (Task 8)

---

## Testing Strategy {#testing-strategy}

### Unit Tests

**Coverage Target:** 90%+

**Test Categories:**
1. **Prompt Injection Detection**
   - Known attack patterns
   - Edge cases
   - False positive rate
   - Performance benchmarks

2. **Tool Permission Validation**
   - Valid permissions
   - Invalid permissions
   - Role-based access
   - Permission inheritance

3. **Data Redaction**
   - Secret pattern matching
   - PII detection
   - Redaction accuracy
   - Performance impact

4. **Rate Limiting**
   - Limit enforcement
   - Tenant overrides
   - Distributed scenarios
   - Reset behavior

5. **Sandbox Execution**
   - Resource limits
   - Network isolation
   - Filesystem restrictions
   - Timeout handling

### Integration Tests

**Test Scenarios:**
1. **End-to-End Chat Flow**
   - User input → Prompt guard → LLM → Response filter
   - Verify security checks at each stage
   - Measure total latency impact

2. **Agent Tool Execution**
   - Agent requests tool → Permission check → Sandbox execution
   - Verify HITL integration
   - Test permission denied scenarios

3. **Rate Limit Enforcement**
   - Multiple requests → Rate limit exceeded
   - Verify 429 responses
   - Test tenant overrides

4. **Audit Log Generation**
   - Security event → Audit log entry
   - Verify log completeness
   - Test log rotation

### Property-Based Tests

**Using Hypothesis:**
1. **Prompt Injection Fuzzing**
   - Generate random attack patterns
   - Verify detection or safe handling
   - Find edge cases

2. **Tool Permission Fuzzing**
   - Generate random agent/tool combinations
   - Verify permission logic
   - Find authorization bypasses

3. **Sandbox Escape Attempts**
   - Generate malicious code
   - Verify sandbox containment
   - Test resource limit enforcement

### Security Tests

**Attack Simulations:**
1. **Prompt Injection Attacks**
   - Direct injection
   - Indirect injection (via documents)
   - Multi-turn attacks
   - Obfuscated attacks

2. **Tool Abuse**
   - Unauthorized tool calls
   - Tool chaining attacks
   - Resource exhaustion

3. **Rate Limit Bypass**
   - Multiple accounts
   - Token manipulation
   - Distributed attacks

4. **Sandbox Escape**
   - Network access attempts
   - Filesystem access attempts
   - Resource limit bypass

### Performance Tests

**Benchmarks:**
1. **Prompt Guard Latency:** <50ms per check
2. **Tool Permission Check:** <10ms per check
3. **Data Redaction:** <20ms per response
4. **Sandbox Startup:** <2s per execution
5. **Total Security Overhead:** <100ms per request

---

## Configuration Management

### Environment Variables

**New Variables:**
```env
# Security Configuration
SECURITY_PROMPT_INJECTION_ENABLED=true
SECURITY_PROMPT_INJECTION_ACTION=block  # or warn
SECURITY_TOOL_PERMISSIONS_ENABLED=true
SECURITY_RATE_LIMITING_ENABLED=true
SECURITY_DATA_REDACTION_ENABLED=true
SECURITY_SANDBOX_ENABLED=true
SECURITY_AUDIT_RETENTION_DAYS=90

# Rate Limits (defaults)
RATE_LIMIT_CHAT=10/minute
RATE_LIMIT_SEARCH=30/minute
RATE_LIMIT_DOCUMENTS=20/minute

# Sandbox Configuration
SANDBOX_MEMORY_LIMIT=256m
SANDBOX_CPU_QUOTA=50000
SANDBOX_TIMEOUT=30
SANDBOX_NETWORK_ENABLED=false

# Model Allowlist (comma-separated)
ALLOWED_MODELS=gpt-4o,gpt-4o-mini,claude-3-5-sonnet,gemini-1.5-pro,ollama/llama3.1:8b
```

### Database Schema

**New Tables:**
```sql
-- security_policies
CREATE TABLE security_policies (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    policy_type VARCHAR NOT NULL,  -- prompt_injection, tool_permissions, etc.
    config JSONB NOT NULL,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- rate_limit_overrides
CREATE TABLE rate_limit_overrides (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR NOT NULL,
    limit_per_minute INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- model_costs
CREATE TABLE model_costs (
    id UUID PRIMARY KEY,
    model_name VARCHAR UNIQUE NOT NULL,
    input_cost_per_1k DECIMAL(10, 6) NOT NULL,
    output_cost_per_1k DECIMAL(10, 6) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- security_events (extends existing audit_events)
-- Add index on event_type for security queries
CREATE INDEX idx_audit_events_security 
ON audit_events(event_type) 
WHERE event_type LIKE 'security_%';
```

---

## Deployment Considerations

### Docker Compose Updates

**New Service:**
```yaml
# infrastructure/docker/docker-compose.yml
services:
  sandbox-runner:
    image: python:3.12-slim
    container_name: co-op-sandbox
    networks:
      - co-op-network
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp:size=100M,mode=1777
    mem_limit: 512m
    cpus: 0.5
```

### Migration Path

**Phase 1.5 Rollout:**
1. Deploy security module (non-breaking)
2. Enable prompt guard (warn mode)
3. Monitor for false positives
4. Enable tool permissions (Phase 2 agents)
5. Enable sandbox (when code execution tools added)
6. Switch to block mode after validation

**Backward Compatibility:**
- All security features optional via feature flags
- Existing APIs unchanged
- Security transparent to clients
- Gradual rollout per tenant

---

## Success Metrics

### Security Metrics

1. **Prompt Injection Detection Rate:** >95%
2. **False Positive Rate:** <5%
3. **Tool Permission Violations:** 0 in production
4. **Sandbox Escapes:** 0
5. **Secret Leaks:** 0
6. **Rate Limit Effectiveness:** >99% compliance

### Performance Metrics

1. **Security Overhead:** <100ms per request
2. **Prompt Guard Latency:** <50ms
3. **Tool Permission Check:** <10ms
4. **Sandbox Startup:** <2s
5. **Audit Log Write:** <5ms

### Operational Metrics

1. **Security Events Logged:** 100% coverage
2. **Audit Log Retention:** 90 days
3. **Alert Response Time:** <5 minutes
4. **Security Patch Time:** <24 hours

---

## Next Steps

### Immediate Actions (This Week)

1. **Review and Approve Plan**
   - Stakeholder review
   - Technical review
   - Security review

2. **Set Up Development Environment**
   - Create feature branch: `feature/ai-security`
   - Set up test infrastructure
   - Prepare attack dataset

3. **Begin Implementation**
   - Start with Task 1 (module structure)
   - Implement Task 2 (prompt guard)
   - Implement Task 3 (LLM gateway)

### Week 1 Deliverables

- Security module structure
- Prompt injection guard (working)
- LLM gateway with model allowlist
- Rate limiting (basic)
- Unit tests for above

### Week 2 Deliverables

- Tool permission system
- Agent RBAC definitions
- LangGraph integration
- Audit logging system
- Integration tests

### Week 3 Deliverables

- Data redaction
- Docker sandbox (basic)
- Security configuration
- Documentation
- Performance benchmarks

---

## Conclusion

This implementation plan provides a comprehensive, phased approach to securing Co-Op's AI agents while maintaining the project's core principles of self-hosted, open-source operation. The plan prioritizes high-impact security measures (prompt injection, tool permissions, rate limiting) while deferring advanced features (sandbox, policy-based control) to later phases.

The modular design ensures backward compatibility and allows gradual rollout per tenant, minimizing risk while maximizing security coverage.

**Estimated Total Effort:** 40-50 hours (2-3 weeks for one developer)

**Risk Level:** LOW (non-breaking changes, feature-flagged)

**Impact:** HIGH (addresses 8 critical security gaps)

---

**Document Version:** 1.0  
**Last Updated:** 2027-01-28  
**Status:** READY FOR REVIEW

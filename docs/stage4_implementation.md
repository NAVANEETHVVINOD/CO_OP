# Stage 4 — Scaling to Full v5.3
## Implementation Guide

**What this stage delivers:** Enterprise-grade components added one at a time, only when you feel the specific pain of not having them.

**Services:** Add per trigger (not all at once)

**Timeline:** Month 5 onward

---

## The Golden Rule

> **Never add a Stage 4 component preemptively.**
> Wait until you feel the specific pain described in each trigger.
> If you're not feeling the pain, you don't need the component yet.

---

## Trigger Map

| Pain Signal | Component to Add | Effort |
|-------------|-----------------|--------|
| ARQ loses tasks on container crash | Temporal workflow engine | 8h |
| Agents burn money in infinite loops | Zombie detector (needs Temporal) | 4h |
| Upwork blocks scraping repeatedly | Browserless proxy rotation | 3h |
| Need to debug agent decisions | OpenTelemetry + Grafana Tempo | 6h |
| Docker sandbox feels unsafe | microsandbox (microVM) | 4h |
| npm/pip downloads too slow | Verdaccio + devpi caches | 3h |
| LLM bottleneck at peak hours | vLLM (GPU) or Groq API | 5h |
| Team of 3+ needs permissions | OPA policy engine | 4h |
| Messages lost at high load | NATS JetStream | 4h |
| 50+ clients need graph queries | Neo4j + Graphiti | 6h |
| Revenue > £10k, need HTTPS/scale | Traefik API gateway | 3h |
| Enterprise client needs SSO | Keycloak OIDC | 6h |
| Multi-node reliability needed | Helm charts + Kubernetes | 8h |

---

## Detailed Implementation Guides

### Temporal (When ARQ Isn't Durable Enough)

**Trigger:** You notice that ARQ loses a task when the API container restarts mid-workflow. A proposal was being processed and simply vanished.

```yaml
# Add to docker-compose.yml
temporal:
  image: temporalio/auto-setup:1.24
  ports: ["7233:7233"]
  environment:
    - DB=postgresql
    - DB_PORT=5432
    - POSTGRES_USER=coop
    - POSTGRES_PWD=${DB_PASS}
    - POSTGRES_SEEDS=postgres

temporal-ui:
  image: temporalio/ui:2.26
  ports: ["8088:8080"]
  environment:
    - TEMPORAL_ADDRESS=temporal:7233
```

**Migration path:** Start by moving the proposal pipeline from ARQ to Temporal. Keep ARQ for simple crons (morning brief, system monitor). Gradually migrate more workflows as needed.

**Verify:** Kill the worker mid-proposal → restart → proposal resumes from where it left off.

### Zombie Detector (When Agents Burn Money)

**Trigger:** An agent gets stuck in an infinite loop and burns $50 in LLM tokens before you notice.

**Implementation:** A cron that checks all running Temporal workflows. If any workflow has been running > 2× its average duration for that type, it:
1. Pauses LiteLLM calls for that agent
2. Snapshots the workflow state
3. Sends a Telegram alert with the cost so far

**Requires:** Temporal must be running first.

### OpenTelemetry + Grafana (When You Need Debugging)

**Trigger:** You can't figure out why an agent made a particular decision last Tuesday. You need to see every step, every LLM call, every tool call with timing.

```yaml
# Add to docker-compose.yml
otel-collector:
  image: otel/opentelemetry-collector:latest
  ports: ["4317:4317"]

grafana-tempo:
  image: grafana/tempo:latest
  ports: ["3200:3200"]

prometheus:
  image: prom/prometheus:latest
  ports: ["9090:9090"]

grafana:
  image: grafana/grafana:latest
  ports: ["3001:3000"]
```

**Instrument:** Add OpenTelemetry spans to LangGraph nodes, ARQ tasks, and API routes. Each agent run gets a trace ID that you can search in Grafana.

### microsandbox (When Docker Sandbox Isn't Secure Enough)

**Trigger:** A client submits suspicious code and Docker sandbox feels insufficient. You want microVM-level isolation.

**Requirements:** KVM must be enabled on your machine (`/dev/kvm` must exist).

**Migration:** Replace `docker_sandbox.py` with microsandbox client. The API stays the same — only the sandbox backend changes.

---

## Hardware Scaling Guide

| Revenue Level | Recommended Setup | Monthly Cost |
|--------------|-------------------|--------------|
| £0-1k | Your laptop or Hetzner CX21 (8GB) | €5/month |
| £1-5k | Hetzner CX31 (16GB) | €9/month |
| £5-10k | Hetzner AX42 (64GB, GPU optional) | €55/month |
| £10k+ | Dedicated server or multi-node | €100+/month |

---

## Decision Framework

Before adding any Stage 4 component, ask yourself:

1. **Am I feeling this pain right now?** (Not hypothetically — right now)
2. **How much time/money is this pain costing me?** (Quantify it)
3. **Is there a simpler workaround?** (Often there is)
4. **How long will setup take vs how much pain it solves?** (ROI check)

If the answer to #1 is "no" → stop. Come back when it's "yes."

---

## Common Pitfalls

1. **Adding Temporal too early** — ARQ handles everything until you have multi-day workflows that crash mid-execution.
2. **Running all observability at once** — Start with just OpenTelemetry + Grafana. Add Prometheus + Loki only if you need metrics and log aggregation.
3. **Choosing vLLM without a GPU** — vLLM needs a CUDA-capable GPU. Without one, use Groq API instead.
4. **Neo4j before 50 clients** — PostgreSQL JSONB handles simple relationship queries just fine. Neo4j only wins for complex graph traversals.
5. **Kubernetes before multi-node** — Docker Compose with Traefik handles single-node deployments perfectly. Only move to K8s when you need multiple servers.

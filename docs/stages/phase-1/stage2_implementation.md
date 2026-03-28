# Stage 2 — Real Intelligence
## Implementation Guide

**What this stage delivers:** Real LLM responses, Telegram control panel, background task workers, and a Lead Scout agent that reads Upwork job listings.

**Services (8):** + ollama, litellm

**Timeline:** Month 2 (4 weeks)

---

## What You Get

- Real LLM-generated answers grounded in your documents
- Per-agent daily token limits enforced via LiteLLM
- Telegram bot: /status, /pause, /panic, /approve commands
- Live thinking display as agents work
- System Monitor checking health every 5 minutes
- Lead Scout reading Upwork every 4 hours
- Morning brief at 8am via Telegram
- Hardware detection recommending the right model for your machine

---

## Key Architectural Decisions

### Why ARQ Instead of Celery?

| | ARQ | Celery |
|--|-----|--------|
| Config | Zero | 400+ lines |
| Async native | Yes (asyncio) | Needs gevent/eventlet |
| Broker | Redis (already have it) | Redis or RabbitMQ |
| Workers | Runs inside API container | Needs separate container |
| Best for | 4 agents on one machine | 50+ agents across nodes |

ARQ is the right choice until Stage 4. Switch to Celery+NATS only if you outgrow it.

### Why Ollama + LiteLLM (Not Direct API Calls)?

LiteLLM sits between your code and the LLM. Benefits:
- **Budget enforcement**: per-agent daily token limits
- **Task routing**: simple tasks → fast 3B model, complex → 8B model
- **Swap models later**: change `litellm_config.yaml`, no code changes
- **Add cloud fallback later**: add Groq/Gemini as overflow without touching agent code

### Why Telegram (Not Slack/Discord)?

- Works on mobile without corporate accounts
- Bot API is simple — python-telegram-bot library handles everything
- You can respond to your system from anywhere
- Easy to add Discord/Slack later in Stage 3 Communication service

### Why No Separate ARQ Container?

ARQ runs as a second process inside the co-op-api container using supervisord or a shell script. This avoids:
- Another Docker container to manage
- Shared volume mounts for code
- Container networking between workers and API

When you outgrow this (Stage 4), split into a dedicated worker container.

---

## Implementation Steps

### Week 1: Local LLM

```bash
# 1. Add Ollama to docker-compose.yml
# ollama: image: ollama/ollama:latest, port 11434, volume for models

# 2. Pull models
docker exec ollama ollama pull llama3.2:3b   # Fast (simple tasks)
docker exec ollama ollama pull llama3.1:8b   # Quality (proposals)

# 3. Create litellm_config.yaml
# Route simple → 3B, standard → 8B, set per-agent budgets

# 4. Add LiteLLM to docker-compose.yml
# litellm: ghcr.io/berriai/litellm:latest, port 4000

# 5. Update generate_answer in nodes.py to call LiteLLM
```

### Week 2: ARQ Workers

```python
# services/api/app/worker.py
import arq
from arq.connections import RedisSettings

async def system_monitor_task(ctx):
    """Check all services every 5 minutes"""
    # Check Docker containers, API health, Redis queue
    # Self-heal if possible, alert Telegram if not

class WorkerSettings:
    functions = [system_monitor_task]
    redis_settings = RedisSettings()
    cron_jobs = [
        arq.cron(system_monitor_task, minute={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55})
    ]
```

```bash
# Update Dockerfile entrypoint to run both:
# uvicorn app.main:app --host 0.0.0.0 --port 8000
# python -m arq app.worker.WorkerSettings
# Use supervisord or a shell script with & and wait
```

### Week 3: Telegram Bot

```python
# services/api/app/communication/telegram.py
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler

async def start(update: Update, context):
    await update.message.reply_text("Co-Op is running. Send /help for commands.")

async def status(update: Update, context):
    health = await check_system_health()
    await update.message.reply_text(format_health(health))

# Commands: /status, /pause, /resume, /panic, /approve, /budget, /help
```

### Week 4: First Agent

```python
# services/api/app/agent/lead_scout.py
async def lead_scout_task(ctx, company_id: str):
    """Runs every 4 hours to find matching Upwork jobs"""
    profile = await get_company_profile(company_id)
    jobs = await search_upwork_via_httpx(profile.skills, profile.target_clients)
    scored = [(score_job(j, profile), j) for j in jobs]
    top5 = sorted(scored, reverse=True)[:5]
    await notify_telegram(format_job_findings(top5))
```

---

## How to Verify Stage 2 Is Complete

| Check | Command / Action | Expected Result |
|-------|-----------------|-----------------|
| Ollama running | `curl localhost:11434/api/tags` | Lists models |
| LiteLLM running | `curl localhost:4000/health` | `{"status":"healthy"}` |
| Real LLM answers | Ask question in /chat | Coherent, reasoned response |
| Hardware detection | `curl /api/settings/hardware` | Shows correct tier |
| ARQ worker running | `docker compose logs co-op-api` | ARQ worker logs visible |
| System Monitor | Stop a container | Telegram alert within 60s |
| Telegram /status | Send /status to bot | System health response |
| Lead Scout | Wait for cron or trigger | Telegram message with jobs |
| Morning brief | Check at 8am | Summary message in Telegram |
| Backup | Check at 2am | pg_dump + qdrant snapshot exists |
| GitHub tag | Check Tags | v0.2.0 visible |

---

## Common Pitfalls

1. **Model download takes time** — Llama 3.1 8B is ~5GB. Be patient.
2. **ARQ cron timezone** — ARQ uses UTC by default. Set your timezone in WorkerSettings.
3. **Telegram bot token exposure** — Keep TELEGRAM_BOT_TOKEN in .env, never commit it.
4. **LiteLLM budget exceeded** — When budget hits limit, agents get 429 errors. Set sensible daily limits (e.g., 100k tokens/agent/day).
5. **httpx being blocked by Upwork** — Expected. This is exactly the pain that triggers adding Browserless in Stage 3.

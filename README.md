# Co-Op: Autonomous Company OS (v1.0) 🚀

Co-Op is the world's first fully autonomous company operating system, designed to scout leads, write proposals, manage projects, and handle finance with human-in-the-loop oversight.

# 🌟 Co-Op Autonomous Company OS v1.0.0 🌟

Co-Op is an AI-native operating system designed to run an autonomous company. It integrates lead scouting, proposal writing, and financial management into a seamless, high-performance platform.

---

## 🚀 Quick Start (One-Click Install)

Get up and running in minutes on any platform.

### Windows (PowerShell)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/navaneethvvinod/co_op/main/install.ps1'))
```

### Linux & macOS (Bash)
```bash
curl -sSL https://raw.githubusercontent.com/navaneethvvinod/co_op/main/install.sh | bash
```

---

## 📚 Documentation

Detailed guides for every stage of your journey:

- [📥 **Installation Guide**](docs/INSTALL.md) - Platform-specific notes and manual setup.
- [📖 **User Guide**](docs/USAGE.md) - How to use the CLI, desktop app, and agents.
- [🛠️ **Development Guide**](docs/DEVELOPMENT.md) - Contributing and extending Co-Op.

---

## 📦 Features

- **Lead Scout**: AI agent that discovers business opportunities.
- **Proposal Writer**: RAG-enhanced agent for high-conversion drafting.
- **Finance Manager**: Automated invoicing and revenue tracking.
- **Native Desktop App**: Tray controls, background monitoring, and native notifications.
- **CLI Tool**: Powerful management from the terminal.
- **HITL (Human-in-the-Loop)**: Review and approve all agent actions globally.
- **Observability**: Built-in Sentry tracking and persistent diagnostic logging.
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

If you want an AI that actually does the work, not just talk about it, this is it.

**Preferred setup:** run `coop onboard` in your terminal. Co-Op Onboard guides you step‑by‑step through setting up the gateway, agents, channels, and company profile. Works on macOS, Linux, and Windows (via WSL2; strongly recommended). New install? Start here: [Getting started](#quick-start-5-minutes).

## What Co-Op Does

Co-Op is a self‑hosted AI platform that turns your laptop or server into an autonomous business operator. It connects to your messaging apps (Telegram, WhatsApp, Discord, Email), searches for clients, writes personalized proposals, delivers code or content, tracks projects, and sends invoices — all with your final approval.

- **Lead Scout** – Searches Upwork, LinkedIn, and Fiverr every few hours, scores jobs against your profile.
- **Proposal Writer** – Drafts personalized proposals using your portfolio (RAG), self‑reviews for quality.
- **Developer Agent** – Writes code, runs tests in a sandbox, pushes to GitHub, and opens a browser‑based VS Code for your review.
- **Client Communicator** – Handles professional conversations, escalates complex issues to you.
- **Project Tracker** – Sets milestones, sends deadline reminders, tracks deliverables.
- **Finance Manager** – Creates invoices from completed milestones, tracks payments, sends reminders.
- **System Monitor** – Watches all services, attempts self‑heal, alerts you on Telegram.
- **Self‑Improvement Analyst** – Reviews win/loss patterns, proposes improvements, tests them in a shadow environment.

**Everything runs locally** – no cloud dependency, no hidden fees. You stay in control.

## Quick Start (5 minutes)

### Prerequisites
- Docker (with Docker Compose) – [Install](https://docs.docker.com/get-docker/)
- 4 GB RAM (8 GB recommended for Stages 2+)
- Git

### 1. Install Co-Op
```bash
curl -fsSL https://co-op.ai/install.sh | bash
```
*Or, if you prefer to clone:*
```bash
git clone https://github.com/NAVANEETHVVINOD/CO_OP.git
cd CO_OP
./install.sh
```

### 2. Run the Onboarding Wizard
```bash
coop onboard --install-daemon
```
The wizard will:
- Detect your hardware (CPU, RAM, GPU, KVM)
- Ask about your business (conversation, template, or custom)
- Connect your Telegram (or other channels)
- Install a background service (systemd/launchd) so Co-Op runs 24/7

### 3. Check the Dashboard
After onboarding, open [http://localhost:3000](http://localhost:3000).
Default login: `admin@co-op.local` / `testpass123` *(change after first login)*.

### 4. Start Earning
- Upload your portfolio documents → the agents will use them.
- Lead Scout will start searching for jobs.
- Proposals will appear in your Telegram or dashboard for approval.
- Approved proposals are submitted automatically.
- When you win a project, the workflow begins.

## How It Grows (4 Stages)

Co-Op starts with a lightweight foundation and adds features only when you need them.

| Stage | Services | What You Get |
|-------|----------|--------------|
| 1 | 6 | RAG chatbot, document upload, dark dashboard |
| 2 | 8 | Real LLM (Ollama), Telegram commands, Lead Scout |
| 3 | 12 | Proposals submitted, client communication, invoicing |
| 4 | (add when needed) | Code delivery, microVM sandbox, graph memory, temporal workflows |

**Full details:** [Architecture Blueprint](docs/CO_OP_SOLO_DEVELOPER_ARCHITECTURE.md)

## Architecture (10‑Layer Diagram)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LAYER 0: HARDWARE DETECTION                          │
│  Detects CPU, RAM, GPU, KVM → assigns tier (Solo / Team / Agency)          │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LAYER 1: GATEWAY DASHBOARD (Next.js 15)               │
│  Dark theme dashboard with live agent activity, approval inbox, cost       │
│  tracker, company builder, and settings.                                   │
│  Communication: Server‑Sent Events (SSE) for streaming chat.               │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LAYER 2: COMMUNICATION HUB (FastAPI)                  │
│  Adapters: Telegram Bot, Discord Bot, WhatsApp Business, Email (SMTP).    │
│  All platforms support slash commands: /status, /pause, /panic, /approve. │
│  Thinking display shows agent progress in real time.                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 LAYER 3: API GATEWAY & SECURITY                             │
│  Traefik (TLS, rate limiting), LLM Guard (prompt injection detection),     │
│  HashiCorp Vault (secrets), OPA (action authorization - Stage 4).          │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LAYER 4: COMPANY BRAIN (FastAPI)                       │
│  Stores business profile, goals, constraints.                               │
│  Strategic Planner: reads KPIs, generates weekly plans.                    │
│  Research Agent: scans GitHub, HuggingFace, arXiv for improvements.        │
│  Agent Factory: creates new agents from natural language descriptions.     │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LAYER 5: AGENT WORKFORCE (LangGraph)                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ Lead Scout  │ │Proposal     │ │Client       │ │ Developer Agent     │   │
│  │ (searches   │ │ Writer      │ │Communicator │ │ (writes & tests     │   │
│  │  jobs)      │ │ (drafts)    │ │ (replies)   │ │  code)              │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │Project      │ │Finance      │ │Quality      │ │ System Monitor      │   │
│  │ Tracker     │ │ Manager     │ │ Reviewer    │ │ (health checks)     │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LAYER 6: WORKFLOW & TASK ENGINE                         │
│  ARQ (async Redis queue) – handles short parallel tasks (Stage 1-3).       │
│  Celery / Temporal (Stage 4) – durable multi-day workflows.                │
│  Cron Scheduler (Celery Beat) – system monitors, morning brief, backups.   │
│  Shadow Environment – isolated test stack for safe self‑improvement.       │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LAYER 7: INTERNET & TOOL LAYER                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Tool Router (FastAPI)                          │   │
│  │  POST /tools/execute → checks OPA → selects executor → audit        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│       │                 │                 │                 │               │
│  ┌────▼────┐      ┌────▼────┐      ┌────▼────┐      ┌────▼────┐           │
│  │Browser‑ │      │Composio │      │ micro‑  │      │ GitHub  │           │
│  │ less    │      │ MCP     │      │ sandbox │      │ API     │           │
│  │ (web    │      │ (500+   │      │ (code   │      │ (repos, │           │
│  │automation)│     │integrat.)│      │execution)│     │ PRs)    │           │
│  └─────────┘      └─────────┘      └─────────┘      └─────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 8: KNOWLEDGE & MEMORY                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  HOT     │  │  WARM    │  │  COLD    │  │KNOWLEDGE │  │ DOCUMENTS│     │
│  │ (Redis)  │  │(Postgres)│  │ (Graphiti│  │(Qdrant)  │  │ (MinIO)  │     │
│  │ Session  │  │ Clients, │  │ + Neo4j) │  │ Portfolio│  │Files,    │     │
│  │ context  │  │proposals │  │Relations│  │templates │  │research  │     │
│  │          │  │results   │  │patterns │  │research  │  │delivera‑ │     │
│  │          │  │          │  │          │  │          │  │bles      │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│  Memory Governor: loads only 50 most relevant facts per agent invocation.   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 9: INFERENCE ENGINE (LiteLLM)                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Task Router:                                                        │   │
│  │    Simple tasks (classification) → Llama 3.2 3B (local, fast)       │   │
│  │    Standard tasks (proposals) → Llama 3.1 8B (local)                │   │
│  │    Complex tasks → Groq / Gemini API (optional, fallback)           │   │
│  │  Budget enforcement: per‑agent daily token limits, hard stop.        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Capabilities

**1. Lead Generation**
- Lead Scout runs every 4 hours (configurable) and searches job boards (Upwork, LinkedIn, Fiverr) using Browserless or official APIs.
- Scores each job (0‑10) based on your profile and skills.
- Sends top matches to your Telegram with a summary.

**2. Proposal Writing**
- Proposal Writer retrieves relevant portfolio pieces from Qdrant.
- Uses your company tone and success patterns to draft personalized proposals.
- Self‑reviews for length, specificity, and client fit.
- Queues proposals for your approval (Telegram or dashboard).

**3. Code & Content Delivery**
- Developer Agent can write code using Claude or GPT‑4o (external AI as tools) or local models.
- Code is tested in a temporary sandbox (Docker, or microVM in Stage 4).
- You review the code in a browser‑based VS Code (code‑server).
- Once approved, it pushes to GitHub and delivers to the client.

**4. Client Communication**
- Client Communicator maintains conversation history in PostgreSQL.
- Responds professionally, never claims to be human.
- Escalates complaints, price negotiations, and scope changes to you.

**5. Project Management**
- Project Tracker creates milestones from the proposal.
- Sends deadline reminders 72 hours in advance.
- Generates weekly status reports for you to approve before sending to clients.

**6. Invoicing & Payments**
- Finance Manager creates invoices from completed milestones.
- You review and approve → invoice is sent via email.
- Tracks payment status, sends reminders after 7 days.

**7. Self‑Improvement**
- Self‑Improvement Analyst reviews win/loss patterns weekly.
- Tests new prompts or strategies in a shadow environment (fake clients).
- Proposes improvements to you with evidence from the shadow test.
- You approve, and the system updates its own configuration.

**8. Human‑in‑the‑Loop (HITL)**
- All mutating actions (proposals, invoices, code pushes) require your explicit approval.
- Approve via Telegram slash commands (`/approve 1 3`) or dashboard.
- You can pause any agent or the whole system with `/pause` or `/panic`.

## CLI Reference

| Command | Description |
|---------|-------------|
| `coop onboard` | Interactive wizard (hardware detection, company creation, channel linking, daemon) |
| `coop gateway start` | Start all Docker services |
| `coop gateway stop` | Stop all services |
| `coop status` | Quick overview: agents, queue, costs |
| `coop doctor` | Full health check + security audit |
| `coop agents list` | List all agents and their status |
| `coop agents pause` | Pause all agents |
| `coop approve <id>` | Approve a pending HITL action |
| `coop panic` | Emergency stop (all agents halt) |
| `coop backup` | Run backup now (PostgreSQL, Qdrant, MinIO) |

Full CLI docs: [CLI Reference](docs/CO_OP_SOLO_TASKS_UPDATED.md) *(docs structure WIP)*

## Security Defaults

Co-Op connects to real messaging surfaces. Inbound messages are treated as untrusted input.
- Telegram / WhatsApp / Discord / Email: unknown senders receive a pairing code and their message is not processed until you approve the sender.
- Approve with: `coop pairing approve <channel> <code>`
- To allow open DMs, set `dmPolicy="open"` in configuration *(not recommended)*.
- Run `coop doctor` to surface risky policies.
- All secrets are stored in HashiCorp Vault (Stage 3). By default, credentials are kept in `.env` for simplicity.

## Installation Options

### Docker (Recommended)
```bash
git clone https://github.com/NAVANEETHVVINOD/CO_OP.git
cd CO_OP
./install.sh
```

### From Source (Development)
```bash
git clone https://github.com/NAVANEETHVVINOD/CO_OP.git
cd CO_OP
pnpm install   # if you want to build frontend locally
cd infrastructure/docker
docker compose up -d
```

## 🛠️ Management CLI

The `coop` CLI tool is the primary way to manage your Autonomous Company OS.

### Installation
```bash
pip install -e ./cli
```

### Usage
- **Gateway Control**:
  - `coop gateway start` – Start all services
  - `coop gateway stop` – Stop all services
  - `coop gateway status` – Check health
- **Diagnostics**:
  - `coop doctor` – Run system check
- **Billing & HITL**:
  - `coop approve <approval_id>` – Approve a queued action
- **Verification**:
  - `coop test` – Run the E2E "Gold Path" verification suite
- **Backup**:
  - `coop backup create` – Create a system snapshot

### Windows (WSL2)
We strongly recommend running Co-Op inside WSL2 for the best experience. Follow the [Windows guide](docs/windows-guide.md).

## Documentation

- [Architecture Blueprint](docs/CO_OP_SOLO_DEVELOPER_ARCHITECTURE.md) – full staged architecture, hardware tiers
- [Task List](docs/CO_OP_SOLO_TASKS_UPDATED.md) – 83 tasks across 4 stages with “Done when” conditions
- [Stage 1 Implementation](docs/stage1_implementation.md) – foundation setup
- [Stage 2 Implementation](docs/stage2_implementation.md) – LLM + Telegram + Lead Scout
- [Stage 3 Implementation](docs/stage3_implementation.md) – proposals, client comms, invoicing
- [Stage 4 Implementation](docs/stage4_implementation.md) – scaling triggers (add only when needed)
- [Rules & Constraints](docs/rules/co-op-coding-standards.mdc) – coding standards, agent behaviour, constraints

## Contributing

Co-Op follows the solo developer philosophy – start simple, add complexity only when needed. Before contributing:
1. Read `docs/rules/co-op-solo-guidelines.mdc`
2. Understand the 4 stages – do not add enterprise features prematurely
3. Follow the coding standards in `docs/rules/co-op-coding-standards.mdc`
4. Run `coop doctor` to ensure your environment is healthy

Pull requests are welcome! Whether you're fixing a bug, improving documentation, or adding a new skill, please open an issue first to discuss.

## License

Apache License 2.0 – See [LICENSE](LICENSE) file.

## Acknowledgments
- **LangGraph** for agent state machines
- **LiteLLM** for LLM gateway
- **Browserless** for headless Chrome
- **OpenClaw** for inspiration on CLI onboarding

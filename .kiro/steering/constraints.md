---
inclusion: auto
---

# Critical Constraints — Never Violate These 8 Rules

## Rule 1: NO API KEYS REQUIRED

```
❌ NO Ollama installation required
❌ NO OpenAI API key
❌ NO Claude/Anthropic API key
❌ NO HuggingFace paid tier
```

The chat endpoint uses **stubbed inference** — it assembles answers from RAG chunks without calling any LLM. This is intentional and working.

**DO NOT add any LLM calls unless explicitly instructed by the user.**

When ready to add a real LLM, the change is ONE LINE in `litellm_config.yaml`. Everything else stays the same.

## Rule 2: NEVER TOUCH THE WORKING PYTHON BACKEND

The Python backend in `services/api/` is complete and verified working.

**DO NOT modify any Python files unless:**
- Fixing a specific bug with a known error message
- The user explicitly asks you to modify a specific file

When told to "fix" something backend-related, read the error message carefully and make the minimum change needed. Do not refactor working code.

## Rule 3: PHASE DISCIPLINE — Build Only Current Phase

Build ONLY Phase 0 services. Do NOT add services from future phases.

**Phase 0 (current):** 6 services
- co-op-api (FastAPI)
- co-op-web (Next.js)
- postgres
- redis
- qdrant
- minio

**Phase 1 (NOT YET):** Keycloak, LLM Guard, Traefik, Temporal, RAGFlow
**Phase 2 (NOT YET):** Kubernetes, Composio MCP, HITL full flow
**Phase 3 (NOT YET):** Graphiti, Vault, Istio, CrewAI

## Rule 4: NO PLACEHOLDERS

Every file must be complete. Never write:
- `// TODO: implement this`
- `pass` statements in functions that should have logic
- Stub functions that just return `None`
- `// Coming soon` comments
- Incomplete implementations

## Rule 5: ENVIRONMENT VARIABLES ONLY

Never hardcode:
- Passwords
- Secret keys
- Connection strings
- API keys

Always use environment variables from `.env` files.

## Rule 6: DOCKER SERVICE NAMES (NOT localhost)

Inside Docker Compose, services communicate using service names:

```yaml
✅ CORRECT:
DATABASE_URL: postgresql+asyncpg://coop:${DB_PASS}@postgres:5432/coop
REDIS_URL: redis://redis:6379
QDRANT_URL: http://qdrant:6333
MINIO_ENDPOINT: minio:9000

❌ WRONG:
DATABASE_URL: postgresql+asyncpg://coop:${DB_PASS}@localhost:5432/coop
REDIS_URL: redis://localhost:6379
```

`localhost` only works for accessing services FROM the host machine, not between Docker containers.

## Rule 7: useChat.ts IS WORKING — DO NOT REWRITE IT

The file `apps/web/src/hooks/useChat.ts` is already working and handles SSE streaming correctly.

**Import it. Never rewrite it. Never replace it.**

## Rule 8: ALWAYS SHOW COMPLETE FILES

When showing file contents, always show the COMPLETE file.

Never say:
- "the rest remains the same"
- "add this to the existing file" (without showing full context)
- "... (rest of file unchanged)"

Always provide the full file content so changes can be verified in context.

## SSE Event Format (Never Change This)

The frontend `useChat.ts` expects EXACTLY this format:

```
event: citation
data: {"source": "file.pdf", "page": 4, "score": 0.94}

event: token
data: {"content": "text here"}

event: done
data: {"conversation_id": "uuid", "cost_usd": 0}
```

Do not modify this format without updating both backend and frontend simultaneously.

## When to Ask vs Just Do

### Just Do It (no need to ask):
- Fixing a bug with a specific error message
- Adding missing npm/pip packages
- Creating or updating TypeScript interfaces to match API
- Fixing TypeScript type errors from `pnpm build`
- Adding missing env vars to docker-compose

### Ask Before Doing:
- Dropping or recreating database tables
- Changing the RAG pipeline logic
- Modifying `useChat.ts`
- Adding new Docker services
- Changing authentication logic
- Upgrading major library versions

### Never Do Without Explicit Instruction:
- Delete any production data
- Change the Qdrant collection schema
- Add any LLM API key configuration
- Move to Phase 1+ services

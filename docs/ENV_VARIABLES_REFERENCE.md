# Environment Variables Reference

This document provides an overview of all environment variable configuration files in Co-Op OS v1.0.3.

## Configuration Files Overview

Co-Op OS uses multiple `.env.example` files for different deployment scenarios:

### 1. Root `.env.example`
**Location:** `.env.example`  
**Purpose:** Reference documentation showing all environment variables across the entire system  
**Use Case:** Understanding the complete configuration landscape

### 2. Docker Deployment `.env.example`
**Location:** `infrastructure/docker/.env.example`  
**Purpose:** Complete Docker deployment configuration  
**Use Case:** Production and development Docker deployments  
**Copy to:** `infrastructure/docker/.env`

### 3. Backend API `.env.example`
**Location:** `services/api/.env.example`  
**Purpose:** Backend API configuration for standalone development  
**Use Case:** Backend-only development without Docker  
**Copy to:** `services/api/.env`

### 4. Frontend Web `.env.example`
**Location:** `apps/web/.env.example`  
**Purpose:** Frontend configuration for standalone development  
**Use Case:** Frontend-only development without Docker  
**Copy to:** `apps/web/.env.local`

## Variable Categories

### Required Variables (All Deployments)
- `DATABASE_URL` - PostgreSQL connection string
- `DB_PASS` - PostgreSQL password
- `REDIS_URL` - Redis connection URL
- `MINIO_URL` - MinIO object storage endpoint
- `MINIO_ROOT_USER` - MinIO username
- `MINIO_ROOT_PASSWORD` - MinIO password
- `SECRET_KEY` - JWT signing key (min 32 chars)
- `OLLAMA_URL` - Ollama LLM service endpoint
- `API_BASE_URL` - Backend API URL
- `FRONTEND_URL` - Frontend URL
- `NEXT_PUBLIC_API_URL` - API URL for browser (frontend)

### Optional Service URLs
- `LITELLM_URL` - LiteLLM gateway endpoint
- `QDRANT_URL` - Qdrant vector database endpoint

### Feature Flags
- `USE_QDRANT` - Enable Qdrant vector search (true/false)
- `COOP_SIMULATION_MODE` - Enable simulation mode (true/false)
- `ENVIRONMENT` - Environment name (local/development/staging/production)

### Observability
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `SENTRY_DSN` - Sentry error tracking DSN (optional)

### Stage 2 Features (Optional)
- `TELEGRAM_BOT_TOKEN` - Telegram bot token for notifications
- `TELEGRAM_ADMIN_CHAT_ID` - Telegram chat ID for admin alerts
- `GROQ_API_KEY` - Groq API key for LLM access
- `GEMINI_API_KEY` - Google Gemini API key
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key (used by LiteLLM)

### Frontend-Specific (Development)
- `NEXT_PUBLIC_DEFAULT_EMAIL` - Default login email (dev only)
- `NEXT_PUBLIC_DEFAULT_PASSWORD` - Default login password (dev only)
- `NEXT_PUBLIC_ENVIRONMENT` - Frontend environment

### CLI Configuration (Optional)
- `COOP_COMPOSE_PATH` - Path to docker-compose.yml
- `COOP_ENV_FILE` - Path to .env file
- `COOP_API_URL` - API URL for CLI commands

## Validation

All `.env.example` files have been verified to include:
- ✅ All variables from `services/api/app/config.py` Settings class
- ✅ All variables from `apps/web/src/lib/env.ts`
- ✅ All variables used in `infrastructure/docker/docker-compose.yml`
- ✅ All CLI environment variables documented in `cli/README.md`

## Quick Start

### Docker Deployment
```bash
cp infrastructure/docker/.env.example infrastructure/docker/.env
# Edit infrastructure/docker/.env with your values
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

### Backend Development
```bash
cp services/api/.env.example services/api/.env
# Edit services/api/.env with your values
cd services/api && uvicorn app.main:app --reload
```

### Frontend Development
```bash
cp apps/web/.env.example apps/web/.env.local
# Edit apps/web/.env.local with your values
cd apps/web && pnpm dev
```

## Security Notes

- Never commit `.env` files to version control
- Change all default passwords and secrets in production
- Use strong, randomly generated values for `SECRET_KEY`
- Remove development defaults in production (`DEFAULT_EMAIL`, `DEFAULT_PASSWORD`)
- Keep API keys and tokens secure
- Regularly rotate secrets and credentials

## See Also

- [CLI Configuration](../cli/README.md) - Detailed CLI environment variable documentation
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [Project Structure](PROJECT_STRUCTURE.md) - Complete project organization

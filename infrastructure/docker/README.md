# Docker Infrastructure

Co-Op uses Docker Compose for container orchestration with a microservices architecture. All services are containerized for consistent deployment across development, staging, and production environments.

## Table of Contents

- [Overview](#overview)
- [Service Architecture](#service-architecture)
- [Environment Variables](#environment-variables)
- [Deployment Guide](#deployment-guide)
- [Networking](#networking)
- [Security](#security)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Overview

The Co-Op infrastructure consists of 6 core services orchestrated by Docker Compose:

- **co-op-web** - Next.js 16 frontend application
- **co-op-api** - FastAPI backend with RAG pipeline
- **postgres** - PostgreSQL 16 database with pgvector extension
- **redis** - Redis 7 for caching and task queues
- **minio** - S3-compatible object storage for documents
- **litellm** - LLM gateway for unified inference API

### Technology Stack

- Docker 24.0+ with Compose V2
- Container images pinned to specific versions for security
- Health checks for all services
- Resource limits for stability
- Security hardening with capability dropping

### Quick Start

```bash
# Clone repository
git clone https://github.com/NAVANEETHVVINOD/CO_OP.git
cd CO_OP/infrastructure/docker

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f
```

## Service Architecture

```mermaid
graph TB
    subgraph "External Access"
        USER[User Browser]
        API_CLIENT[API Client]
    end
    
    subgraph "Application Layer"
        WEB[co-op-web<br/>Next.js 16<br/>Port 3000]
        API[co-op-api<br/>FastAPI<br/>Port 8000]
    end
    
    subgraph "Data Layer"
        PG[(postgres<br/>PostgreSQL 16<br/>Port 5433)]
        REDIS[(redis<br/>Redis 7<br/>Port 6379)]
        MINIO[(minio<br/>MinIO<br/>Ports 9000/9001)]
    end
    
    subgraph "AI Layer"
        LITELLM[litellm<br/>LLM Gateway<br/>Port 4000]
    end
    
    subgraph "Persistent Storage"
        PG_VOL[postgres_data]
        REDIS_VOL[redis_data]
        MINIO_VOL[minio_data]
    end
    
    USER -->|HTTP| WEB
    API_CLIENT -->|HTTP/REST| API
    WEB -->|HTTP/SSE| API
    
    API -->|SQL| PG
    API -->|Cache/Queue| REDIS
    API -->|S3 API| MINIO
    API -->|Inference| LITELLM
    
    PG -.->|Mount| PG_VOL
    REDIS -.->|Mount| REDIS_VOL
    MINIO -.->|Mount| MINIO_VOL
    
    style WEB fill:#4CAF50
    style API fill:#2196F3
    style PG fill:#336791
    style REDIS fill:#DC382D
    style MINIO fill:#E91E63
    style LITELLM fill:#795548
    style PG_VOL fill:#E0E0E0
    style REDIS_VOL fill:#E0E0E0
    style MINIO_VOL fill:#E0E0E0
```

### Service Details

#### co-op-web (Frontend)

Next.js 16 application with React 19 and Server Components.

**Image:** Built from `apps/web/Dockerfile` (development) or `ghcr.io/navaneethvvinod/co-op-web:v1.0.3` (production)

**Ports:**
- 3000 - HTTP server

**Dependencies:**
- co-op-api (HTTP API)

**Resources:**
- Memory limit: 256 MB
- Memory reservation: 128 MB

**Health Check:** None (Next.js handles graceful startup)

**Security:**
- Capabilities dropped: ALL
- No new privileges
- Runs as non-root user

#### co-op-api (Backend)

FastAPI application with async SQLAlchemy, LangGraph agents, and RAG pipeline.

**Image:** Built from `services/api/Dockerfile` (development) or `ghcr.io/navaneethvvinod/co-op-api:v1.0.3` (production)

**Ports:**
- 8000 - HTTP API server

**Dependencies:**
- postgres (database)
- redis (cache/queue)
- minio (object storage)
- litellm (LLM gateway)

**Resources:**
- Memory limit: 1 GB
- Memory reservation: 512 MB

**Health Check:**
- Endpoint: `http://localhost:8000/health`
- Interval: 30s
- Timeout: 10s
- Retries: 10
- Start period: 300s (5 minutes for migrations)

**Security:**
- Capabilities dropped: ALL
- No new privileges
- Temporary filesystem: /tmp (tmpfs)

#### postgres (Database)

PostgreSQL 16 with pgvector extension for vector similarity search.

**Image:** `pgvector/pgvector:pg16`

**Ports:**
- 5433 (host) → 5432 (container) - PostgreSQL server

**Volumes:**
- `postgres_data:/var/lib/postgresql/data` - Database files
- `./init.sql:/docker-entrypoint-initdb.d/init.sql` - Initialization script

**Resources:**
- Memory limit: 512 MB
- Memory reservation: 256 MB

**Health Check:**
- Command: `pg_isready -U coop`
- Interval: 10s
- Timeout: 5s
- Retries: 5

**Security:**
- Capabilities dropped: ALL
- Capabilities added: SETUID, SETGID, DAC_READ_SEARCH
- No new privileges

**Configuration:**
- Database: coop
- User: coop
- Password: From `DB_PASS` environment variable
- Auth method: trust (for Docker network)

#### redis (Cache & Queue)

Redis 7 for session caching, task queues, and pub/sub messaging.

**Image:** `redis:7.2.5-alpine`

**Ports:**
- 6379 - Redis server

**Volumes:**
- `redis_data:/data` - Persistent data with AOF

**Command:** `redis-server --appendonly yes`

**Resources:**
- Memory limit: 128 MB
- Memory reservation: 64 MB

**Health Check:**
- Command: `redis-cli ping`
- Interval: 10s
- Timeout: 5s
- Retries: 5

**Security:**
- Capabilities dropped: ALL
- Capabilities added: SETUID, SETGID, CHOWN
- No new privileges

**Configuration:**
- Persistence: AOF (Append-Only File)
- No password (internal network only)

#### minio (Object Storage)

MinIO S3-compatible object storage for document files.

**Image:** `minio/minio:RELEASE.2024-06-04T19-20-08Z`

**Ports:**
- 9000 - S3 API
- 9001 - Web console

**Volumes:**
- `minio_data:/data` - Object storage

**Command:** `server /data --console-address ":9001"`

**Resources:**
- Memory limit: 256 MB
- Memory reservation: 128 MB

**Health Check:**
- Endpoint: `http://localhost:9000/minio/health/live`
- Interval: 10s
- Timeout: 5s
- Retries: 5

**Security:**
- Capabilities dropped: ALL
- Capabilities added: SETUID, SETGID, CHOWN
- No new privileges

**Configuration:**
- Root user: From `MINIO_ROOT_USER` environment variable
- Root password: From `MINIO_ROOT_PASSWORD` environment variable
- Default bucket: coop-documents (created by API on startup)

#### litellm (LLM Gateway)

LiteLLM proxy for unified LLM API access.

**Image:** `ghcr.io/berriai/litellm:main` (pinned for security - see CVE-2026-33634 note)

**Ports:**
- 4000 - HTTP API

**Volumes:**
- `./litellm_config.yaml:/app/config.yaml:ro` - Configuration file (read-only)

**Command:** `--config /app/config.yaml --port 4000`

**Resources:**
- Memory limit: 256 MB
- Memory reservation: 128 MB

**Health Check:**
- Endpoint: `http://localhost:4000/health`
- Interval: 15s
- Timeout: 5s
- Retries: 5

**Security:**
- Capabilities dropped: ALL
- No new privileges

**Configuration:**
- API keys: From environment variables (GROQ_API_KEY, GEMINI_API_KEY, etc.)
- Config file: `litellm_config.yaml` with model routing

**Security Note:** LiteLLM is pinned to a specific version due to CVE-2026-33634. Do NOT use `main-latest` or floating tags. Before upgrading, verify the new image does not contain malicious `.pth` files.

## Environment Variables

### Required Variables

Create a `.env` file in `infrastructure/docker/` with the following variables:

```bash
# Database
DB_PASS=your_secure_password_here

# MinIO S3 Storage
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_password_here
MINIO_URL=http://minio:9000

# Redis
REDIS_URL=redis://redis:6379

# LiteLLM
LITELLM_URL=http://litellm:4000

# API Configuration
SECRET_KEY=your_secret_key_here_min_32_chars
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
LOG_LEVEL=INFO

# Optional: LLM API Keys (leave empty for stubbed inference)
GROQ_API_KEY=
GEMINI_API_KEY=
OLLAMA_URL=

# Optional: Telegram Bot
TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_ID=

# Optional: Monitoring
SENTRY_DSN=

# Feature Flags
USE_QDRANT=false
COOP_SIMULATION_MODE=true

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_EMAIL=admin@co-op.local
NEXT_PUBLIC_DEFAULT_PASSWORD=testpass123
NEXT_PUBLIC_ENVIRONMENT=development
```

### Variable Reference

#### Database Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DB_PASS | Yes | - | PostgreSQL password for 'coop' user |
| DATABASE_URL | Auto | postgresql+asyncpg://coop:${DB_PASS}@postgres:5432/coop | Full database connection URL |

#### Storage Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| MINIO_ROOT_USER | Yes | minioadmin | MinIO admin username |
| MINIO_ROOT_PASSWORD | Yes | - | MinIO admin password (min 8 chars) |
| MINIO_URL | Yes | http://minio:9000 | MinIO S3 API endpoint |
| MINIO_ENDPOINT | Auto | ${MINIO_URL} | Alias for MINIO_URL |

#### Cache Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| REDIS_URL | Yes | redis://redis:6379 | Redis connection URL |

#### API Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| SECRET_KEY | Yes | - | JWT signing key (min 32 chars) |
| API_BASE_URL | Yes | http://localhost:8000 | API base URL for CORS |
| FRONTEND_URL | Yes | http://localhost:3000 | Frontend URL for CORS |
| ENVIRONMENT | No | development | Environment: development, staging, production |
| LOG_LEVEL | No | INFO | Logging level: DEBUG, INFO, WARNING, ERROR |

#### LLM Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| LITELLM_URL | Yes | http://litellm:4000 | LiteLLM gateway URL |
| GROQ_API_KEY | No | - | Groq API key for fast inference |
| GEMINI_API_KEY | No | - | Google Gemini API key |
| OLLAMA_URL | No | - | Ollama local inference URL |
| COOP_SIMULATION_MODE | No | true | Use stubbed LLM responses (no API key needed) |

#### Feature Flags

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| USE_QDRANT | No | false | Enable Qdrant vector database (Phase 1+) |
| QDRANT_URL | No | - | Qdrant server URL |

#### Frontend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| NEXT_PUBLIC_API_URL | Yes | http://localhost:8000 | API URL for client-side requests |
| NEXT_PUBLIC_DEFAULT_EMAIL | No | admin@co-op.local | Default login email (dev only) |
| NEXT_PUBLIC_DEFAULT_PASSWORD | No | testpass123 | Default login password (dev only) |
| NEXT_PUBLIC_ENVIRONMENT | No | development | Environment for client-side logic |

#### Monitoring Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| SENTRY_DSN | No | - | Sentry error tracking DSN |
| TELEGRAM_BOT_TOKEN | No | - | Telegram bot token for notifications |
| TELEGRAM_ADMIN_CHAT_ID | No | - | Telegram chat ID for admin alerts |

## Deployment Guide

### Development Deployment

For local development with hot reloading:

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f co-op-api co-op-web

# Restart specific service
docker compose restart co-op-api

# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

### Production Deployment

For production deployment with pre-built images:

1. **Update docker-compose.yml** to use versioned images:

```yaml
services:
  co-op-api:
    image: ghcr.io/navaneethvvinod/co-op-api:v1.0.3
    # Remove 'build' section

  co-op-web:
    image: ghcr.io/navaneethvvinod/co-op-web:v1.0.3
    # Remove 'build' section
```

2. **Configure production environment:**

```bash
# Copy production template
cp .env.production .env

# Edit with production values
nano .env

# Set secure passwords
DB_PASS=$(openssl rand -base64 32)
MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 32)
```

3. **Deploy services:**

```bash
# Pull latest images
docker compose pull

# Start services
docker compose up -d

# Verify health
docker compose ps
docker compose logs co-op-api | grep "Application startup complete"
```

4. **Run database migrations:**

```bash
# Migrations run automatically on API startup
# Verify in logs:
docker compose logs co-op-api | grep "Running migrations"
```

### Production Best Practices

1. **Use specific version tags** - Never use `latest` tag in production
2. **Enable TLS/SSL** - Use reverse proxy (Traefik, Nginx) for HTTPS
3. **Secure secrets** - Use Docker secrets or external secret management
4. **Resource limits** - Adjust memory limits based on workload
5. **Monitoring** - Enable Sentry, Prometheus, or other monitoring
6. **Backups** - Automate database and MinIO backups
7. **Log aggregation** - Use centralized logging (ELK, Loki)
8. **Health checks** - Monitor service health endpoints
9. **Update strategy** - Use blue-green or rolling deployments
10. **Disaster recovery** - Test backup restoration regularly

### Scaling Considerations

For high-traffic deployments:

```yaml
services:
  co-op-api:
    deploy:
      replicas: 3  # Multiple API instances
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    
  postgres:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

Add load balancer:

```yaml
services:
  traefik:
    image: traefik:v3.2
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

## Networking

### Network Architecture

```mermaid
graph TB
    subgraph "Host Network"
        HOST[Host Machine<br/>localhost]
    end
    
    subgraph "Docker Bridge Network: default"
        WEB[co-op-web<br/>Internal: 3000]
        API[co-op-api<br/>Internal: 8000]
        PG[postgres<br/>Internal: 5432]
        REDIS[redis<br/>Internal: 6379]
        MINIO[minio<br/>Internal: 9000/9001]
        LITELLM[litellm<br/>Internal: 4000]
    end
    
    HOST -->|3000| WEB
    HOST -->|8000| API
    HOST -->|5433| PG
    HOST -->|6379| REDIS
    HOST -->|9000/9001| MINIO
    HOST -->|4000| LITELLM
    
    WEB -->|HTTP| API
    API -->|SQL| PG
    API -->|TCP| REDIS
    API -->|HTTP| MINIO
    API -->|HTTP| LITELLM
    
    style HOST fill:#FFF3E0
    style WEB fill:#4CAF50
    style API fill:#2196F3
    style PG fill:#336791
    style REDIS fill:#DC382D
    style MINIO fill:#E91E63
    style LITELLM fill:#795548
```

### Port Mappings

| Service | Internal Port | Host Port | Protocol | Purpose |
|---------|---------------|-----------|----------|---------|
| co-op-web | 3000 | 3000 | HTTP | Frontend application |
| co-op-api | 8000 | 8000 | HTTP | Backend API |
| postgres | 5432 | 5433 | TCP | PostgreSQL database |
| redis | 6379 | 6379 | TCP | Redis cache/queue |
| minio | 9000 | 9000 | HTTP | S3 API |
| minio | 9001 | 9001 | HTTP | Web console |
| litellm | 4000 | 4000 | HTTP | LLM gateway |

### Service Discovery

Services communicate using Docker DNS:

```python
# Backend connects to database using service name
DATABASE_URL = "postgresql+asyncpg://coop:password@postgres:5432/coop"

# Backend connects to Redis using service name
REDIS_URL = "redis://redis:6379"

# Backend connects to MinIO using service name
MINIO_URL = "http://minio:9000"
```

### Network Isolation

For production, create isolated networks:

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
  data:
    driver: bridge
    internal: true  # No external access

services:
  co-op-web:
    networks:
      - frontend
  
  co-op-api:
    networks:
      - frontend
      - backend
      - data
  
  postgres:
    networks:
      - data
  
  redis:
    networks:
      - data
  
  minio:
    networks:
      - data
```

## Security

### Container Hardening

All containers follow security best practices:

1. **Capability Dropping** - Remove all Linux capabilities by default
2. **No New Privileges** - Prevent privilege escalation
3. **Non-Root User** - Run as unprivileged user where possible
4. **Read-Only Filesystem** - Mount volumes as read-only when possible
5. **Resource Limits** - Prevent resource exhaustion attacks

### Secrets Management

**Development:**
```bash
# Use .env file (not committed to git)
echo ".env" >> .gitignore
```

**Production:**
```bash
# Use Docker secrets
echo "my_db_password" | docker secret create db_pass -

# Reference in compose file
services:
  postgres:
    secrets:
      - db_pass
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass

secrets:
  db_pass:
    external: true
```

### Network Security

1. **Firewall Rules:**
```bash
# Allow only necessary ports
ufw allow 3000/tcp  # Frontend
ufw allow 8000/tcp  # API
ufw deny 5432/tcp   # Block direct database access
ufw deny 6379/tcp   # Block direct Redis access
```

2. **TLS/SSL:**
```yaml
services:
  traefik:
    command:
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    volumes:
      - ./letsencrypt:/letsencrypt
```

### Security Scanning

```bash
# Scan images for vulnerabilities
docker scout cves co-op-api:latest

# Scan running containers
trivy image co-op-api:latest

# Check for secrets in images
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image co-op-api:latest
```

## Monitoring

### Health Checks

All services have health checks configured:

```bash
# Check service health
docker compose ps

# View health check logs
docker inspect co-op-api | jq '.[0].State.Health'
```

### Logs

```bash
# View all logs
docker compose logs

# Follow specific service
docker compose logs -f co-op-api

# View last 100 lines
docker compose logs --tail=100 co-op-api

# Filter by timestamp
docker compose logs --since 2024-01-15T10:00:00 co-op-api
```

### Resource Usage

```bash
# View resource usage
docker stats

# View specific service
docker stats co-op-api

# Export metrics
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Prometheus Metrics

Add Prometheus exporter:

```yaml
services:
  prometheus:
    image: prom/prometheus:v2.45.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
```

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs for errors
docker compose logs co-op-api

# Check health status
docker compose ps

# Restart service
docker compose restart co-op-api

# Rebuild and restart
docker compose up -d --build co-op-api
```

#### Database Connection Errors

```bash
# Verify postgres is healthy
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U coop -d coop -c "SELECT 1;"

# Verify environment variables
docker compose exec co-op-api env | grep DATABASE_URL
```

#### MinIO Connection Errors

```bash
# Check MinIO health
curl http://localhost:9000/minio/health/live

# Verify credentials
docker compose exec co-op-api env | grep MINIO

# Check bucket exists
docker compose exec minio mc ls local/coop-documents
```

#### Out of Memory Errors

```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  co-op-api:
    deploy:
      resources:
        limits:
          memory: 2G

# Restart with new limits
docker compose up -d
```

#### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
services:
  co-op-api:
    ports:
      - "8001:8000"
```

### Debugging Commands

```bash
# Enter container shell
docker compose exec co-op-api bash

# Run command in container
docker compose exec co-op-api python -c "import sys; print(sys.version)"

# Copy files from container
docker compose cp co-op-api:/app/logs/app.log ./logs/

# Inspect container configuration
docker inspect co-op-api

# View container processes
docker compose top co-op-api
```

### Performance Tuning

```bash
# Optimize PostgreSQL
docker compose exec postgres psql -U coop -d coop -c "
  ALTER SYSTEM SET shared_buffers = '256MB';
  ALTER SYSTEM SET effective_cache_size = '1GB';
  ALTER SYSTEM SET maintenance_work_mem = '64MB';
  SELECT pg_reload_conf();
"

# Optimize Redis
docker compose exec redis redis-cli CONFIG SET maxmemory 128mb
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## SEO Keywords

Docker Compose deployment, microservices architecture, container orchestration, self-hosted infrastructure, PostgreSQL Docker, Redis Docker, MinIO S3 storage, FastAPI Docker, Next.js Docker, Docker security hardening, container health checks, Docker networking, production deployment, Docker monitoring


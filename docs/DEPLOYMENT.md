# Co-Op Deployment Guide

This document provides comprehensive deployment instructions for Co-Op across different environments: development, staging, and production.

## Table of Contents

- [Overview](#overview)
- [Deployment Architecture](#deployment-architecture)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Network Configuration](#network-configuration)
- [Security Hardening](#security-hardening)
- [Monitoring and Observability](#monitoring-and-observability)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Overview

Co-Op supports multiple deployment strategies:

- **Local Development** - Docker Compose on localhost
- **Single Server** - Docker Compose on VPS/dedicated server
- **Multi-Server** - Distributed deployment with load balancing
- **Kubernetes** - Container orchestration for large-scale deployments

This guide focuses on Docker Compose deployments, which are suitable for most use cases.

## Deployment Architecture

### Docker Compose Architecture

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "Frontend Network"
            WEB[co-op-web<br/>Next.js<br/>:3000]
        end
        
        subgraph "Backend Network"
            API[co-op-api<br/>FastAPI<br/>:8000]
            WORKER[arq-worker<br/>Background Tasks]
            CRON[cron-jobs<br/>Scheduled Tasks]
        end
        
        subgraph "Data Network"
            PG[(postgres<br/>PostgreSQL 16<br/>:5432)]
            RD[(redis<br/>Redis 7<br/>:6379)]
            QD[(qdrant<br/>Qdrant 1.12<br/>:6333)]
            MO[(minio<br/>MinIO<br/>:9000/:9001)]
        end
        
        subgraph "AI Network"
            OL[ollama<br/>Local LLM<br/>:11434]
            LL[litellm<br/>LLM Gateway<br/>:4000]
        end
        
        subgraph "Volumes"
            PG_VOL[postgres_data]
            QD_VOL[qdrant_data]
            MO_VOL[minio_data]
            RD_VOL[redis_data]
        end
    end
    
    HOST[Host Machine<br/>localhost] -->|3000| WEB
    HOST -->|8000| API
    HOST -->|5433| PG
    HOST -->|6379| RD
    HOST -->|6333| QD
    HOST -->|9000/9001| MO
    
    WEB -->|HTTP| API
    API -->|SQL| PG
    API -->|Cache| RD
    API -->|Vector| QD
    API -->|S3| MO
    API -->|Enqueue| RD
    RD -->|Dequeue| WORKER
    WORKER -->|SQL| PG
    WORKER -->|Vector| QD
    WORKER -->|S3| MO
    CRON -->|Monitor| API
    CRON -->|Backup| PG
    CRON -->|Backup| QD
    CRON -->|Backup| MO
    API -->|Inference| LL
    LL -->|Local| OL
    
    PG -.->|Mount| PG_VOL
    QD -.->|Mount| QD_VOL
    MO -.->|Mount| MO_VOL
    RD -.->|Mount| RD_VOL
    
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
    style PG_VOL fill:#E0E0E0
    style QD_VOL fill:#E0E0E0
    style MO_VOL fill:#E0E0E0
    style RD_VOL fill:#E0E0E0
```

### Production Deployment Architecture

```mermaid
graph TB
    subgraph "External"
        USER[Users]
        DNS[DNS]
    end
    
    subgraph "Edge Layer"
        LB[Load Balancer<br/>Traefik/Nginx]
        SSL[SSL/TLS<br/>Let's Encrypt]
    end
    
    subgraph "Application Layer"
        WEB1[co-op-web-1]
        WEB2[co-op-web-2]
        API1[co-op-api-1]
        API2[co-op-api-2]
        WORKER1[worker-1]
        WORKER2[worker-2]
    end
    
    subgraph "Data Layer"
        PG_PRIMARY[(PostgreSQL<br/>Primary)]
        PG_REPLICA[(PostgreSQL<br/>Replica)]
        REDIS_PRIMARY[(Redis<br/>Primary)]
        REDIS_REPLICA[(Redis<br/>Replica)]
        QDRANT[(Qdrant<br/>Cluster)]
        MINIO[(MinIO<br/>Cluster)]
    end
    
    subgraph "Backup Layer"
        S3[S3 Backup<br/>Daily Snapshots]
    end
    
    USER --> DNS
    DNS --> SSL
    SSL --> LB
    LB --> WEB1
    LB --> WEB2
    WEB1 --> API1
    WEB2 --> API2
    API1 --> PG_PRIMARY
    API2 --> PG_PRIMARY
    API1 --> REDIS_PRIMARY
    API2 --> REDIS_PRIMARY
    API1 --> QDRANT
    API2 --> QDRANT
    API1 --> MINIO
    API2 --> MINIO
    REDIS_PRIMARY --> WORKER1
    REDIS_PRIMARY --> WORKER2
    PG_PRIMARY -.->|Replication| PG_REPLICA
    REDIS_PRIMARY -.->|Replication| REDIS_REPLICA
    PG_PRIMARY -.->|Backup| S3
    QDRANT -.->|Backup| S3
    MINIO -.->|Backup| S3
    
    style USER fill:#E3F2FD
    style LB fill:#FFF3E0
    style WEB1 fill:#4CAF50
    style WEB2 fill:#4CAF50
    style API1 fill:#2196F3
    style API2 fill:#2196F3
    style WORKER1 fill:#FF9800
    style WORKER2 fill:#FF9800
    style PG_PRIMARY fill:#336791
    style PG_REPLICA fill:#5C8DB8
    style REDIS_PRIMARY fill:#DC382D
    style REDIS_REPLICA fill:#E57373
    style QDRANT fill:#00BCD4
    style MINIO fill:#E91E63
    style S3 fill:#FF9800
```

### Network Diagram

```mermaid
graph LR
    subgraph "Public Network"
        INTERNET[Internet]
    end
    
    subgraph "DMZ"
        LB[Load Balancer<br/>:80/:443]
    end
    
    subgraph "Application Network"
        WEB[Frontend<br/>:3000]
        API[Backend<br/>:8000]
    end
    
    subgraph "Data Network (Internal Only)"
        PG[(PostgreSQL<br/>:5432)]
        RD[(Redis<br/>:6379)]
        QD[(Qdrant<br/>:6333)]
        MO[(MinIO<br/>:9000)]
    end
    
    INTERNET -->|HTTPS| LB
    LB -->|HTTP| WEB
    LB -->|HTTP| API
    WEB -->|HTTP| API
    API -->|TCP| PG
    API -->|TCP| RD
    API -->|HTTP| QD
    API -->|HTTP| MO
    
    style INTERNET fill:#E3F2FD
    style LB fill:#FFF3E0
    style WEB fill:#4CAF50
    style API fill:#2196F3
    style PG fill:#336791
    style RD fill:#DC382D
    style QD fill:#00BCD4
    style MO fill:#E91E63
```

## Development Deployment

### Prerequisites

- Docker 24.0+ with Compose V2
- 4 GB RAM minimum (8 GB recommended)
- 20 GB disk space
- Git

### Quick Start

1. **Clone repository:**
   ```bash
   git clone https://github.com/NAVANEETHVVINOD/CO_OP.git
   cd CO_OP
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

3. **Start services:**
   ```bash
   cd infrastructure/docker
   docker compose up -d
   ```

4. **Verify deployment:**
   ```bash
   docker compose ps
   docker compose logs -f co-op-api
   ```

5. **Access application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001

### Development Environment Variables

```bash
# Database
DB_PASS=dev_password_change_me

# MinIO S3 Storage
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=dev_password_change_me
MINIO_URL=http://minio:9000

# Redis
REDIS_URL=redis://redis:6379

# LiteLLM
LITELLM_URL=http://litellm:4000

# API Configuration
SECRET_KEY=dev_secret_key_min_32_chars_change_me
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Feature Flags
USE_QDRANT=false
COOP_SIMULATION_MODE=true

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_EMAIL=admin@co-op.local
NEXT_PUBLIC_DEFAULT_PASSWORD=testpass123
NEXT_PUBLIC_ENVIRONMENT=development
```

### Development Workflow

**Start services:**
```bash
docker compose up -d
```

**View logs:**
```bash
docker compose logs -f co-op-api co-op-web
```

**Restart specific service:**
```bash
docker compose restart co-op-api
```

**Rebuild after code changes:**
```bash
docker compose up -d --build co-op-api
```

**Stop services:**
```bash
docker compose down
```

**Clean slate (remove volumes):**
```bash
docker compose down -v
```

## Production Deployment

### Prerequisites

- Ubuntu 22.04 LTS or similar Linux distribution
- Docker 24.0+ with Compose V2
- 8 GB RAM minimum (16 GB recommended)
- 50 GB SSD
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

### Production Setup

1. **Prepare server:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo apt install docker-compose-plugin
   
   # Configure firewall
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

2. **Clone and configure:**
   ```bash
   git clone https://github.com/NAVANEETHVVINOD/CO_OP.git
   cd CO_OP
   cp .env.example .env
   ```

3. **Generate secure secrets:**
   ```bash
   # Generate database password
   DB_PASS=$(openssl rand -base64 32)
   echo "DB_PASS=$DB_PASS" >> .env
   
   # Generate MinIO password
   MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)
   echo "MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD" >> .env
   
   # Generate API secret key
   SECRET_KEY=$(openssl rand -base64 32)
   echo "SECRET_KEY=$SECRET_KEY" >> .env
   ```

4. **Configure production environment:**
   ```bash
   # Edit .env file
   nano .env
   ```

   Production environment variables:
   ```bash
   # Database
   DB_PASS=<generated_password>
   
   # MinIO S3 Storage
   MINIO_ROOT_USER=admin
   MINIO_ROOT_PASSWORD=<generated_password>
   MINIO_URL=http://minio:9000
   
   # Redis
   REDIS_URL=redis://redis:6379
   
   # API Configuration
   SECRET_KEY=<generated_secret>
   API_BASE_URL=https://api.yourdomain.com
   FRONTEND_URL=https://yourdomain.com
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   
   # Feature Flags
   USE_QDRANT=true
   COOP_SIMULATION_MODE=false
   
   # Frontend
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   NEXT_PUBLIC_ENVIRONMENT=production
   
   # Optional: LLM API Keys
   GROQ_API_KEY=<your_groq_key>
   GEMINI_API_KEY=<your_gemini_key>
   
   # Optional: Monitoring
   SENTRY_DSN=<your_sentry_dsn>
   TELEGRAM_BOT_TOKEN=<your_telegram_token>
   TELEGRAM_ADMIN_CHAT_ID=<your_chat_id>
   ```

5. **Use production images:**
   
   Edit `infrastructure/docker/docker-compose.yml`:
   ```yaml
   services:
     co-op-api:
       image: ghcr.io/navaneethvvinod/co-op-api:v1.0.3
       # Remove 'build' section
   
     co-op-web:
       image: ghcr.io/navaneethvvinod/co-op-web:v1.0.3
       # Remove 'build' section
   ```

6. **Deploy services:**
   ```bash
   cd infrastructure/docker
   docker compose pull
   docker compose up -d
   ```

7. **Verify deployment:**
   ```bash
   docker compose ps
   docker compose logs co-op-api | grep "Application startup complete"
   ```

8. **Configure reverse proxy (Nginx):**
   ```nginx
   # /etc/nginx/sites-available/co-op
   server {
       listen 80;
       server_name yourdomain.com;
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl http2;
       server_name yourdomain.com;
       
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   
   server {
       listen 443 ssl http2;
       server_name api.yourdomain.com;
       
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

9. **Enable and restart Nginx:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/co-op /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Production Best Practices

1. **Use specific version tags** - Never use `latest` tag
2. **Enable TLS/SSL** - Use Let's Encrypt or commercial certificate
3. **Secure secrets** - Use environment variables, never commit to git
4. **Resource limits** - Configure memory and CPU limits
5. **Monitoring** - Enable Sentry, Prometheus, or similar
6. **Backups** - Automate daily backups of database and volumes
7. **Log aggregation** - Use centralized logging (ELK, Loki)
8. **Health checks** - Monitor service health endpoints
9. **Update strategy** - Use blue-green or rolling deployments
10. **Disaster recovery** - Test backup restoration regularly

### Resource Limits

Configure resource limits in `docker-compose.yml`:

```yaml
services:
  co-op-api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
  
  postgres:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
```

## Network Configuration

### Port Mappings

| Service | Internal Port | Host Port | Protocol | Purpose |
|---------|---------------|-----------|----------|---------|
| co-op-web | 3000 | 3000 | HTTP | Frontend application |
| co-op-api | 8000 | 8000 | HTTP | Backend API |
| postgres | 5432 | 5433 | TCP | PostgreSQL database |
| redis | 6379 | 6379 | TCP | Redis cache/queue |
| qdrant | 6333 | 6333 | HTTP | Qdrant vector database |
| minio | 9000 | 9000 | HTTP | MinIO S3 API |
| minio | 9001 | 9001 | HTTP | MinIO web console |
| litellm | 4000 | 4000 | HTTP | LiteLLM gateway |

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
  
  qdrant:
    networks:
      - data
  
  minio:
    networks:
      - data
```

## Security Hardening

### Container Security

All containers follow security best practices:

```yaml
services:
  co-op-api:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp
```

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

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 5432/tcp  # Block direct database access
sudo ufw deny 6379/tcp  # Block direct Redis access
sudo ufw deny 6333/tcp  # Block direct Qdrant access
sudo ufw deny 9000/tcp  # Block direct MinIO access
sudo ufw enable
```

### SSL/TLS Configuration

**Using Let's Encrypt:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring and Observability

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

### Resource Monitoring

```bash
# View resource usage
docker stats

# View specific service
docker stats co-op-api

# Export metrics
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Application Monitoring

**Sentry Integration:**
```bash
# Add to .env
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

**Prometheus Metrics:**
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

## Backup and Recovery

### Automated Backups

**Database Backup:**
```bash
#!/bin/bash
# backup-postgres.sh
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker compose exec -T postgres pg_dump -U coop coop > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
gzip "$BACKUP_DIR/backup_$TIMESTAMP.sql"
# Keep only last 7 days
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +7 -delete
```

**Qdrant Backup:**
```bash
#!/bin/bash
# backup-qdrant.sh
BACKUP_DIR="/backups/qdrant"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker compose exec -T qdrant tar czf - /qdrant/storage > "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
# Keep only last 7 days
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete
```

**MinIO Backup:**
```bash
#!/bin/bash
# backup-minio.sh
BACKUP_DIR="/backups/minio"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker compose exec -T minio tar czf - /data > "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
# Keep only last 7 days
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete
```

**Cron Schedule:**
```bash
# Add to crontab
0 2 * * * /path/to/backup-postgres.sh
0 3 * * * /path/to/backup-qdrant.sh
0 4 * * * /path/to/backup-minio.sh
```

### Restore Procedures

**Restore Database:**
```bash
gunzip backup_20240115_020000.sql.gz
docker compose exec -T postgres psql -U coop coop < backup_20240115_020000.sql
```

**Restore Qdrant:**
```bash
docker compose stop qdrant
docker compose exec -T qdrant tar xzf - -C / < backup_20240115_030000.tar.gz
docker compose start qdrant
```

**Restore MinIO:**
```bash
docker compose stop minio
docker compose exec -T minio tar xzf - -C / < backup_20240115_040000.tar.gz
docker compose start minio
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

### Performance Tuning

**PostgreSQL Optimization:**
```bash
docker compose exec postgres psql -U coop -d coop -c "
  ALTER SYSTEM SET shared_buffers = '256MB';
  ALTER SYSTEM SET effective_cache_size = '1GB';
  ALTER SYSTEM SET maintenance_work_mem = '64MB';
  SELECT pg_reload_conf();
"
```

**Redis Optimization:**
```bash
docker compose exec redis redis-cli CONFIG SET maxmemory 128mb
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Related Documentation

- [Main README](../README.md) - Project overview
- [Architecture Guide](./ARCHITECTURE.md) - System architecture
- [Docker Infrastructure](../infrastructure/docker/README.md) - Infrastructure details
- [Security Guide](./SECURITY.md) - Security best practices
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions

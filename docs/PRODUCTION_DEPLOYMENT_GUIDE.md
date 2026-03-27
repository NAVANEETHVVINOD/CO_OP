# Production Deployment Guide - Co-Op OS v1.0.3

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/NAVANEETHVVINOD/CO_OP.git
cd CO_OP

# 2. Copy environment file
cp infrastructure/docker/.env.example infrastructure/docker/.env

# 3. Edit configuration
nano infrastructure/docker/.env

# 4. Validate environment
bash infrastructure/docker/validate-env.sh

# 5. Start services
cd infrastructure/docker
docker compose up -d

# 6. Verify health
curl http://localhost:8000/health | jq
```

## Deployment Methods

### Method 1: Docker Compose (Recommended)
- Single-server deployment
- All services in containers
- Suitable for < 100 users

### Method 2: Kubernetes (Future)
- Multi-server deployment
- Horizontal scaling
- Suitable for > 100 users

## Environment Configuration

### Required Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://coop:PASSWORD@postgres:5432/coop
DB_PASS=your_secure_password

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_password
MINIO_URL=minio:9000

# Security
SECRET_KEY=your_32_char_secret_key_here

# Service URLs
OLLAMA_URL=http://ollama:11434
API_BASE_URL=http://co-op-api:8000
FRONTEND_URL=http://co-op-web:3000
REDIS_URL=redis://redis:6379/0
LITELLM_URL=http://litellm:4000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
ENVIRONMENT=production
COOP_SIMULATION_MODE=false
```

## Backup & Recovery

### Database Backup
```bash
# Backup
docker exec postgres pg_dump -U coop coop > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i postgres psql -U coop coop < backup_20270127.sql
```

### MinIO Backup
```bash
# Backup
docker exec minio mc mirror /data /backup

# Restore
docker exec minio mc mirror /backup /data
```

## Upgrade Procedures

### From v1.0.2 to v1.0.3
```bash
# 1. Backup data
bash scripts/backup-all.sh

# 2. Pull latest code
git pull origin main
git checkout v1.0.3

# 3. Update environment
cp infrastructure/docker/.env.example infrastructure/docker/.env.new
# Merge your settings

# 4. Run migrations
docker compose exec co-op-api alembic upgrade head

# 5. Restart services
docker compose restart
```

## Monitoring

### Health Checks
- `/health` - Overall system health with latency
- `/ready` - Readiness probe for load balancers
- `/metrics` - Prometheus metrics (Phase 2)

### Log Locations
- Application: `logs/app.log` (rotated at 10MB)
- Docker: `docker compose logs -f co-op-api`
- System: `/var/log/syslog`

## Troubleshooting

### Services Won't Start
```bash
# Check logs
docker compose logs co-op-api

# Validate environment
bash infrastructure/docker/validate-env.sh

# Check disk space
df -h
```

### Database Connection Errors
```bash
# Check PostgreSQL
docker compose exec postgres psql -U coop -c "SELECT 1"

# Check connection string
echo $DATABASE_URL
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Check service health
curl http://localhost:8000/health | jq '.services'
```

## Security Hardening

### Production Checklist
- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Access control lists

### Network Security
```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 5432/tcp  # PostgreSQL (internal only)
ufw deny 6379/tcp  # Redis (internal only)
```

## Rollback Procedures

### Emergency Rollback
```bash
# 1. Stop services
docker compose down

# 2. Checkout previous version
git checkout v1.0.2

# 3. Restore database
docker exec -i postgres psql -U coop coop < backup_before_upgrade.sql

# 4. Start services
docker compose up -d
```

## Support

- Documentation: https://github.com/NAVANEETHVVINOD/CO_OP/tree/main/docs
- Issues: https://github.com/NAVANEETHVVINOD/CO_OP/issues
- Email: support@co-op-os.ai

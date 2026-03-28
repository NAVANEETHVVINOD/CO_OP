# Troubleshooting

Common issues and their solutions for Co-Op deployment and operation.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Container Issues](#container-issues)
- [Database Issues](#database-issues)
- [API Issues](#api-issues)
- [Frontend Issues](#frontend-issues)
- [Performance Issues](#performance-issues)
- [Testing Issues](#testing-issues)
- [Getting Help](#getting-help)

## Installation Issues

### Docker Compose Not Found

**Symptoms**: `docker compose` command not recognized

**Solutions**:
1. Update Docker Desktop to latest version (includes Compose V2)
2. Install Docker Compose plugin: `sudo apt install docker-compose-plugin`
3. Use legacy command: `docker-compose` (with hyphen)

### Permission Denied (Docker)

**Symptoms**: `permission denied while trying to connect to the Docker daemon socket`

**Solutions**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker

# Verify
docker ps
```

### Port Already in Use

**Symptoms**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solutions**:
```bash
# Find process using the port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
```

## Container Issues

### API Container Fails to Start

**Symptoms**: `docker compose logs co-op-api` shows database connection errors

**Solutions**:

1. **Check PostgreSQL is running**:
```bash
docker compose ps postgres
# Should show "Up" status
```

2. **Verify environment variables**:
```bash
# Check .env file
cat infrastructure/docker/.env | grep POSTGRES
```

3. **Wait for PostgreSQL to be ready**:
```bash
# PostgreSQL may take 10-15 seconds to start
# Check logs
docker compose logs postgres
```

4. **Restart services in order**:
```bash
docker compose up -d postgres redis minio qdrant
sleep 10
docker compose up -d co-op-api
```

### MinIO Health Check Fails

**Symptoms**: `Request URL is missing an 'http://' or 'https://' protocol`

**Solution**: This was fixed in v1.0.3. Ensure you're running the latest version:
```bash
git pull origin main
docker compose up -d --build
```

### Container Exits with Code 137

**Symptoms**: Container stops unexpectedly, exit code 137 in logs

**Cause**: Out of Memory (OOM) kill

**Solutions**:

1. **Increase Docker memory limit**:
   - Docker Desktop → Settings → Resources → Memory
   - Increase to at least 4 GB (8 GB recommended)

2. **Reduce running services**:
```bash
# Disable optional services
docker compose stop ollama litellm
```

3. **Set memory limits in docker-compose.yml**:
```yaml
services:
  co-op-api:
    mem_limit: 512m
    memswap_limit: 512m
```

### Container Logs Show "Connection Refused"

**Symptoms**: API logs show `Connection refused` when connecting to other services

**Solutions**:

1. **Use service names, not localhost**:
   - ✅ `POSTGRES_HOST=postgres`
   - ❌ `POSTGRES_HOST=localhost`

2. **Verify services are on same network**:
```bash
docker network inspect docker_co-op-net
```

3. **Check service health**:
```bash
docker compose ps
# All services should show "healthy" or "Up"
```

## Database Issues

### Migration Fails

**Symptoms**: `alembic upgrade head` fails with error

**Solutions**:

1. **Check current migration version**:
```bash
cd services/api
alembic current
```

2. **Reset database (development only)**:
```bash
docker compose down -v  # WARNING: Deletes all data
docker compose up -d postgres
sleep 10
alembic upgrade head
```

3. **Manual migration**:
```bash
# Connect to database
docker exec -it docker-postgres-1 psql -U coop coop_os

# Check tables
\dt

# Exit
\q
```

### Database Connection Pool Exhausted

**Symptoms**: `QueuePool limit of size 5 overflow 10 reached`

**Solutions**:

1. **Increase pool size** in `app/config.py`:
```python
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
```

2. **Check for connection leaks**:
   - Ensure all `async with session.begin()` blocks complete
   - Use context managers for database sessions

3. **Restart API**:
```bash
docker compose restart co-op-api
```

### Slow Queries

**Symptoms**: API responses are slow, database CPU high

**Solutions**:

1. **Enable query logging**:
```python
# In app/config.py
SQLALCHEMY_ECHO = True
```

2. **Check for missing indexes**:
```sql
-- Connect to database
docker exec -it docker-postgres-1 psql -U coop coop_os

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

3. **Add indexes**:
```bash
# Create migration
alembic revision -m "Add index on documents.status"

# Edit migration file, add:
# op.create_index('ix_documents_status', 'documents', ['status'])

# Apply
alembic upgrade head
```

## API Issues

### 401 Unauthorized

**Symptoms**: API returns 401 for authenticated requests

**Solutions**:

1. **Check token expiration**:
   - Access tokens expire after 15 minutes
   - Use refresh token to get new access token

2. **Verify token format**:
```bash
# Token should be in Authorization header
curl -H "Authorization: Bearer <token>" http://localhost:8000/v1/conversations
```

3. **Check SECRET_KEY**:
   - Ensure `SECRET_KEY` is set and consistent across restarts
   - Changing `SECRET_KEY` invalidates all tokens

### 500 Internal Server Error

**Symptoms**: API returns 500 error

**Solutions**:

1. **Check API logs**:
```bash
docker compose logs co-op-api --tail=100
```

2. **Enable debug mode** (development only):
```python
# In app/main.py
app = FastAPI(debug=True)
```

3. **Check service dependencies**:
```bash
# Test each service
curl http://localhost:8000/health
```

### SSE Streaming Not Working

**Symptoms**: Chat responses don't stream, or connection closes immediately

**Solutions**:

1. **Check reverse proxy configuration**:
   - Nginx: Add `proxy_buffering off;`
   - Ensure timeouts are long enough

2. **Test SSE directly**:
```bash
curl -N -H "Authorization: Bearer <token>" \
  -H "Accept: text/event-stream" \
  http://localhost:8000/v1/chat/stream
```

3. **Check LiteLLM/Ollama**:
```bash
docker compose logs litellm
docker compose logs ollama
```

## Frontend Issues

### Page Not Loading

**Symptoms**: Frontend shows blank page or loading spinner

**Solutions**:

1. **Check browser console** (F12):
   - Look for JavaScript errors
   - Check network tab for failed requests

2. **Verify API connection**:
```bash
# Check NEXT_PUBLIC_API_URL in .env.local
cat apps/web/.env.local
```

3. **Rebuild frontend**:
```bash
cd apps/web
pnpm install
pnpm build
```

### API Requests Failing (CORS)

**Symptoms**: Browser console shows CORS errors

**Solutions**:

1. **Check CORS configuration** in `services/api/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Verify frontend URL**:
   - Ensure `NEXT_PUBLIC_API_URL` points to correct API endpoint

### Build Fails

**Symptoms**: `pnpm build` fails with errors

**Solutions**:

1. **Clear cache**:
```bash
rm -rf .next node_modules
pnpm install
pnpm build
```

2. **Check Node version**:
```bash
node --version  # Should be 20.x or higher
```

3. **Check TypeScript errors**:
```bash
pnpm tsc --noEmit
```

## Performance Issues

### Slow Search / Chat

**Symptoms**: Search or chat responses take >5 seconds

**Solutions**:

1. **Check Qdrant is running**:
```bash
docker compose ps qdrant
curl http://localhost:6333/health
```

2. **Verify embeddings are generated**:
   - Document processing must complete before search works
   - Check document status: `GET /v1/documents`

3. **Enable debug logging**:
```bash
# In docker-compose.yml
environment:
  - LOG_LEVEL=DEBUG
```

4. **Check resource usage**:
```bash
docker stats
```

### High Memory Usage

**Symptoms**: System runs out of memory, containers restart

**Solutions**:

1. **Reduce Qdrant memory**:
```yaml
# In docker-compose.yml
qdrant:
  environment:
    - QDRANT__STORAGE__OPTIMIZERS__MEMMAP_THRESHOLD=20000
```

2. **Disable local LLM**:
```bash
docker compose stop ollama
# Use cloud LLM instead (OpenAI, Anthropic, etc.)
```

3. **Limit document processing**:
   - Process documents in smaller batches
   - Increase chunk size to reduce vector count

## Testing Issues

### Coverage Threshold Not Met

**Symptoms**: CI fails with "coverage below threshold"

**Solutions**:

1. **Run tests locally**:
```bash
cd services/api
pytest --cov=app --cov-report=term-missing
```

2. **Identify uncovered lines**:
   - Look for files with low coverage
   - Add tests for missing lines

3. **Temporarily lower threshold** (not recommended):
```toml
# In pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov-fail-under=70"  # Lower from 80
```

### Tests Fail in CI but Pass Locally

**Symptoms**: Tests pass on local machine but fail in GitHub Actions

**Solutions**:

1. **Check environment differences**:
   - Python version
   - Dependency versions
   - Environment variables

2. **Run tests in Docker**:
```bash
docker compose run --rm co-op-api pytest
```

3. **Check for race conditions**:
   - Use `pytest-xdist` for parallel tests
   - Add delays or retries for flaky tests

### Missing Imports / Module Not Found

**Symptoms**: `ModuleNotFoundError` when running tests

**Solutions**:

1. **Activate virtual environment**:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
# Or
uv pip install -e .
```

3. **Check PYTHONPATH**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Getting Help

### Before Opening an Issue

1. **Search existing issues**: https://github.com/NAVANEETHVVINOD/CO_OP/issues
2. **Check documentation**: Read all relevant docs
3. **Try latest version**: `git pull origin main`
4. **Collect logs**: Save output of `docker compose logs > logs.txt`

### Opening an Issue

Include:
- **OS and version** (Windows 11, Ubuntu 22.04, macOS 14, etc.)
- **Docker version**: `docker --version`
- **Steps to reproduce**: Exact commands that cause the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs**: Relevant log output (use code blocks)
- **Screenshots**: If applicable

### Community Support

- **GitHub Discussions**: https://github.com/NAVANEETHVVINOD/CO_OP/discussions
- **Discord**: (if available)
- **Email**: (if available)

## Related Documentation

- [Installation Guide](../README.md#installation)
- [Docker Infrastructure](../infrastructure/docker/README.md)
- [Database Schema](./DATABASE.md)
- [Security Practices](./SECURITY.md)

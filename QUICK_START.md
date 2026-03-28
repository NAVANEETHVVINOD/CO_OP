# Co-Op OS - Quick Start Guide

## Your System is Running! 🎉

All services are currently running and accessible.

## Access Your Applications

### 1. Web Frontend (READY NOW)
**Open in your browser**: http://localhost:3000

Available pages:
- Dashboard: http://localhost:3000/dashboard
- Login: http://localhost:3000/login
- Signup: http://localhost:3000/signup
- Projects: http://localhost:3000/projects
- Agents: http://localhost:3000/agents
- Documents: http://localhost:3000/documents
- Finance: http://localhost:3000/finance
- Chat: http://localhost:3000/chat

### 2. API Backend (READY NOW)
**API Base URL**: http://localhost:8000

Useful endpoints:
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Desktop Application (Requires Setup)

The desktop app needs to be built first. Here's how:

**Prerequisites**:
1. Install Rust: https://rustup.rs/
2. On Windows, install Visual Studio C++ Build Tools

**Run Desktop App**:
```bash
cd apps/desktop
pnpm install
pnpm tauri dev
```

This will open a native desktop window with the same interface as the web app.

## Current Service Status

✅ **Running Services**:
- PostgreSQL (Database) - Port 5433
- Redis (Cache) - Port 6379
- MinIO (Storage) - Ports 9000-9001
- API Backend - Port 8000
- Web Frontend - Port 3000

⚠️ **Optional Services** (not required for basic functionality):
- LiteLLM (LLM Proxy) - Port 4000
- Qdrant (Vector DB) - Not running
- Ollama (Local LLM) - Not running

## Quick Commands

### Manage Services
```bash
# Check status
docker compose ps

# View logs
docker compose logs -f

# Restart a service
docker compose restart co-op-api

# Stop all services
docker compose down

# Start all services
docker compose up -d
```

### Using CLI Tool
```bash
# Check system health
coop doctor check

# View service status
coop gateway status

# Stop services
coop gateway stop

# Start services
coop gateway start
```

## Next Steps

1. **Access the web interface**: Open http://localhost:3000 in your browser
2. **Create an account**: Go to http://localhost:3000/signup
3. **Explore the dashboard**: Navigate to http://localhost:3000/dashboard
4. **Try the API**: Visit http://localhost:8000/docs for interactive API documentation
5. **Build desktop app** (optional): Follow the desktop app setup instructions above

## Troubleshooting

### Web Frontend Not Loading?
```bash
# Check if container is running
docker compose ps co-op-web

# View logs
docker logs docker-co-op-web-1

# Restart
docker compose restart co-op-web
```

### API Not Responding?
```bash
# Check if container is running
docker compose ps co-op-api

# View logs
docker logs docker-co-op-api-1

# Test health endpoint
curl http://localhost:8000/health
```

### Desktop App Won't Build?
1. Make sure Rust is installed: `rustc --version`
2. Install dependencies: `cd apps/desktop && pnpm install`
3. Check Tauri: `pnpm tauri info`

## Production Readiness Status

✅ All linting errors fixed  
✅ All tests passing (57/57)  
✅ No security vulnerabilities  
✅ Frontend builds successfully  
✅ Docker services running  
✅ API responding  
✅ Database connected  

**Branch**: feature/production-readiness-v1-clean  
**Latest Commit**: d675838e  
**Status**: PRODUCTION READY

## Documentation

- Full Access Guide: `docs/ACCESS_GUIDE.md`
- System Validation: `docs/FINAL_SYSTEM_VALIDATION.md`
- Architecture: `.kiro/steering/architecture.md`
- Project Overview: `.kiro/steering/project.md`

## Support

Need help? Check:
- API Documentation: http://localhost:8000/docs
- System Health: http://localhost:8000/health
- Run diagnostics: `coop doctor check`

---

**Enjoy building with Co-Op OS!** 🚀

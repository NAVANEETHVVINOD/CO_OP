# Co-Op OS Access Guide

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Ports available: 3000 (web), 8000 (API), 5433 (postgres), 6379 (redis), 9000-9001 (minio)

## Accessing the Applications

### 1. Web Frontend (Next.js)

**URL**: http://localhost:3000

**How to Access**:
1. Make sure Docker services are running:
   ```bash
   cd infrastructure/docker
   docker compose up -d
   ```

2. Wait for services to start (check status):
   ```bash
   docker compose ps
   ```

3. Open your browser and navigate to:
   - **Main Dashboard**: http://localhost:3000
   - **Login Page**: http://localhost:3000/login
   - **Signup Page**: http://localhost:3000/signup

**Available Routes**:
- `/` - Landing page
- `/dashboard` - Main dashboard
- `/agents` - Agent management
- `/projects` - Project tracking
- `/documents` - Document management
- `/finance` - Financial overview
- `/approvals` - Approval queue
- `/search` - Search interface
- `/chat` - Chat interface
- `/admin` - Admin panel

### 2. Backend API (FastAPI)

**URL**: http://localhost:8000

**Health Endpoints**:
- **Health Check**: http://localhost:8000/health
- **Ready Check**: http://localhost:8000/ready
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

**Test API**:
```bash
# Check health
curl http://localhost:8000/health

# Check ready status
curl http://localhost:8000/ready

# View API documentation
# Open http://localhost:8000/docs in browser
```

### 3. Desktop Application (Tauri)

**Status**: Desktop app is in development (apps/desktop)

**How to Run Desktop App**:

1. Install Rust and Tauri prerequisites:
   ```bash
   # Install Rust
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   
   # On Windows, also install:
   # - Microsoft Visual Studio C++ Build Tools
   # - WebView2 (usually pre-installed on Windows 10/11)
   ```

2. Navigate to desktop app directory:
   ```bash
   cd apps/desktop
   ```

3. Install dependencies:
   ```bash
   pnpm install
   ```

4. Run in development mode:
   ```bash
   pnpm tauri dev
   ```

5. Build for production:
   ```bash
   pnpm tauri build
   ```

**Desktop App Features**:
- System tray integration
- Native notifications
- Desktop-optimized UI
- Same functionality as web app

**Note**: The desktop app connects to the same backend API (http://localhost:8000), so make sure Docker services are running.

## Service Management

### Using Docker Compose Directly

```bash
# Start all services
cd infrastructure/docker
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f

# Check status
docker compose ps

# Restart a specific service
docker compose restart co-op-api
```

### Using CLI Tool (Recommended)

```bash
# Start services
coop gateway start

# Stop services
coop gateway stop

# Check status
coop gateway status

# Run system diagnostics
coop doctor check
```

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Web Frontend | http://localhost:3000 | Main user interface |
| API Backend | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| PostgreSQL | localhost:5433 | Database |
| Redis | localhost:6379 | Cache & queue |
| MinIO Console | http://localhost:9001 | Object storage UI |
| MinIO API | http://localhost:9000 | Object storage API |
| LiteLLM | http://localhost:4000 | LLM proxy (optional) |

## Default Credentials

### MinIO
- **Username**: minioadmin
- **Password**: minioadmin123
- **Console**: http://localhost:9001

### PostgreSQL
- **Host**: localhost
- **Port**: 5433
- **Database**: coop
- **Username**: postgres
- **Password**: (check .env file for DB_PASS)

### Application
- Create your account via signup page: http://localhost:3000/signup
- Or use the onboarding wizard: `coop onboard setup`

## Troubleshooting

### Frontend Not Loading

1. Check if web container is running:
   ```bash
   docker compose ps co-op-web
   ```

2. Check web logs:
   ```bash
   docker logs docker-co-op-web-1
   ```

3. Verify port 3000 is not in use:
   ```bash
   # Windows
   netstat -ano | findstr :3000
   
   # Linux/Mac
   lsof -i :3000
   ```

### API Not Responding

1. Check if API container is running:
   ```bash
   docker compose ps co-op-api
   ```

2. Check API logs:
   ```bash
   docker logs docker-co-op-api-1
   ```

3. Test health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

### Desktop App Won't Start

1. Verify Rust is installed:
   ```bash
   rustc --version
   cargo --version
   ```

2. Check Tauri CLI:
   ```bash
   cd apps/desktop
   pnpm tauri info
   ```

3. Rebuild dependencies:
   ```bash
   cd apps/desktop
   rm -rf node_modules
   pnpm install
   pnpm tauri dev
   ```

### Database Connection Issues

1. Check PostgreSQL is healthy:
   ```bash
   docker compose ps postgres
   ```

2. Test database connection:
   ```bash
   docker exec docker-postgres-1 psql -U postgres -d coop -c "SELECT 1;"
   ```

3. Check database logs:
   ```bash
   docker logs docker-postgres-1
   ```

## Development Workflow

### Full Stack Development

1. Start backend services:
   ```bash
   cd infrastructure/docker
   docker compose up -d postgres redis minio
   ```

2. Run API in development mode:
   ```bash
   cd services/api
   uvicorn app.main:app --reload --port 8000
   ```

3. Run frontend in development mode:
   ```bash
   cd apps/web
   pnpm dev
   ```

4. Access:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Desktop Development

1. Start backend services (same as above)

2. Run desktop app:
   ```bash
   cd apps/desktop
   pnpm tauri dev
   ```

## Production Deployment

### Using Docker Compose

```bash
# Use production compose file
cd infrastructure/docker
docker compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Make sure to set production environment variables in `.env`:
- `ENVIRONMENT=production`
- `SECRET_KEY=<strong-secret-key>`
- `DATABASE_URL=<production-db-url>`
- `SENTRY_DSN=<your-sentry-dsn>`
- `TELEGRAM_BOT_TOKEN=<your-bot-token>`

## Next Steps

1. Complete onboarding: `coop onboard setup`
2. Access web interface: http://localhost:3000
3. Create your first project
4. Configure agents and workflows
5. Set up integrations (Telegram, Sentry, etc.)

## Support

- Documentation: `docs/` directory
- API Documentation: http://localhost:8000/docs
- Health Status: http://localhost:8000/health
- System Diagnostics: `coop doctor check`

---

**Last Updated**: March 27, 2026  
**Version**: v0.3.0

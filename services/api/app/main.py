from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, auth, documents, search, chat, conversations, approvals, credits, settings, projects, invoices
from .db.session import AsyncSessionLocal, engine
from .db.models import Base, Tenant, User
from .core.security import get_password_hash
from .config import get_settings
from .core.logging import setup_logging
from .core.minio_client import init_minio
from .db.qdrant_client import init_qdrant
from .events.consumer import consume_ingestion_events

from contextlib import asynccontextmanager
import asyncio
import logging
from sqlalchemy import select
from prometheus_fastapi_instrumentator import Instrumentator
from asgi_correlation_id import CorrelationIdMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from .core.rate_limit import limiter

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log configuration on startup
    app_settings = get_settings()
    logger.info("=" * 60)
    logger.info("Co-Op API Starting")
    logger.info("=" * 60)
    logger.info(f"Environment: {app_settings.ENVIRONMENT}")
    logger.info(f"Log Level: {app_settings.LOG_LEVEL}")
    logger.info(f"Simulation Mode: {app_settings.COOP_SIMULATION_MODE}")
    logger.info(f"Database: {app_settings.DATABASE_URL.split('@')[-1] if '@' in app_settings.DATABASE_URL else 'configured'}")
    logger.info(f"Redis: {app_settings.REDIS_URL}")
    logger.info(f"MinIO: {app_settings.MINIO_URL}")
    logger.info(f"Ollama: {app_settings.OLLAMA_URL}")
    logger.info(f"API Base URL: {app_settings.API_BASE_URL}")
    logger.info(f"Frontend URL: {app_settings.FRONTEND_URL}")
    if app_settings.LITELLM_URL:
        logger.info(f"LiteLLM: {app_settings.LITELLM_URL}")
    if app_settings.QDRANT_URL:
        logger.info(f"Qdrant: {app_settings.QDRANT_URL}")
    if app_settings.TELEGRAM_BOT_TOKEN:
        logger.info("Telegram Bot: Enabled")
    if app_settings.SENTRY_DSN:
        logger.info("Sentry: Enabled")
    logger.info("=" * 60)
    
    # Startup: Connect to DB, create tables if needed (simplifying for Phase 0)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Object Storage buckets
    try:
        init_minio()
    except Exception as e:
        logger.warning(f"MinIO init failed (non-fatal): {e}")
    
    # Initialize Qdrant collection
    try:
        await init_qdrant()
    except Exception as e:
        logger.warning(f"Qdrant init failed (non-fatal): {e}")
    
    # Start Redis consumer as background task
    consumer_task = asyncio.create_task(consume_ingestion_events())
    
    # Seed default admin user
    async with AsyncSessionLocal() as session:
        app_settings = get_settings()
        result = await session.execute(select(Tenant).where(Tenant.name == "admin"))
        tenant = result.scalars().first()
        if not tenant:
            tenant = Tenant(name="admin")
            session.add(tenant)
            await session.flush()
            
        result = await session.execute(select(User).where(User.email == "admin@co-op.local"))
        user = result.scalars().first()
        if not user:
            user = User(
                tenant_id=tenant.id,
                email="admin@co-op.local",
                hashed_password=get_password_hash(app_settings.DB_PASS)
            )
            session.add(user)
            await session.commit()

    # --- Stage 2: Hardware detection (non-blocking) ---
    async def _detect_hardware():
        try:
            from .core.hardware_detector import detect_and_store_hardware
            await detect_and_store_hardware()
        except Exception as e:
            logger.warning(f"Hardware detection failed (non-fatal): {e}")

    asyncio.create_task(_detect_hardware())

    # --- Stage 2: Telegram bot (if configured) ---
    telegram_started = False
    try:
        app_settings = get_settings()
        if app_settings.TELEGRAM_BOT_TOKEN:
            from .communication.telegram import start_telegram_bot
            await start_telegram_bot()
            telegram_started = True
        else:
            logger.info("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled.")
    except Exception as e:
        logger.warning(f"Telegram bot startup failed (non-fatal): {e}")

    yield

    # Shutdown
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

    # Stop Telegram bot
    if telegram_started:
        try:
            from .communication.telegram import stop_telegram_bot
            await stop_telegram_bot()
        except Exception as e:
            logger.warning(f"Telegram bot shutdown error: {e}")

    await engine.dispose()

setup_logging()

app_settings = get_settings()
if app_settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=app_settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment=app_settings.ENVIRONMENT,
    )

app = FastAPI(
    title="Co-Op API",
    description="Main Control Plane for Co-Op AI OS",
    version="0.3.0",
    lifespan=lifespan
)

# T-02C: Rate Limiting Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# T-02B: Request IDs
app.add_middleware(CorrelationIdMiddleware)

# T-02B: Prometheus endpoint
Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(approvals.router)
# Stage 2 routers
app.include_router(credits.router)
app.include_router(settings.router)
# Stage 3 routers
app.include_router(projects.router)
app.include_router(invoices.router)

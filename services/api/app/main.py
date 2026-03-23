from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, auth, documents, search, chat, conversations, approvals
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
from sqlalchemy import select
from prometheus_fastapi_instrumentator import Instrumentator
from asgi_correlation_id import CorrelationIdMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .core.rate_limit import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB, create tables if needed (simplifying for Phase 0)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Object Storage buckets
    try:
        init_minio()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"MinIO init failed (non-fatal): {e}")
    
    # Initialize Qdrant collection
    try:
        await init_qdrant()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Qdrant init failed (non-fatal): {e}")
    
    # Start Redis consumer as background task
    consumer_task = asyncio.create_task(consume_ingestion_events())
    
    # Seed default admin user
    async with AsyncSessionLocal() as session:
        settings = get_settings()
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
                hashed_password=get_password_hash(settings.DB_PASS)
            )
            session.add(user)
            await session.commit()
    yield
    # Shutdown
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()

setup_logging()

app = FastAPI(
    title="Co-Op API",
    description="Main Control Plane for Co-Op AI OS",
    version="0.1.0",
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
    allow_origins=["http://localhost:3000"],
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

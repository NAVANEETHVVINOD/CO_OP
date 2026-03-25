import sys
import uuid as _uuid
import sqlite3
from unittest.mock import MagicMock, AsyncMock

# ── Register UUID adapter at the sqlite3 driver level ───────────────────
#    This ensures that any uuid.UUID passed as a parameter to SQLite is
#    automatically converted to hex string.  This is the most reliable
#    approach as it bypasses all SQLAlchemy caching layers.
sqlite3.register_adapter(_uuid.UUID, lambda u: u.hex)
sqlite3.register_converter("CHAR", lambda b: _uuid.UUID(b.decode()) if len(b) == 32 else b.decode())

# ── Patch heavy ML libraries BEFORE any app imports ─────────────────────
class DummySentenceTransformer:
    def __init__(self, *args, **kwargs): pass
    def encode(self, texts, *args, **kwargs): return [[0.0]*384 for _ in texts]

class DummyCrossEncoder:
    def __init__(self, *args, **kwargs): pass
    def predict(self, pairs, *args, **kwargs): return [0.99 for _ in pairs]

mock_st = MagicMock()
mock_st.SentenceTransformer = DummySentenceTransformer
mock_st.CrossEncoder = DummyCrossEncoder
sys.modules['sentence_transformers'] = mock_st

# Override for Redis to prevent connection faults during local testing
import redis.asyncio
def mock_from_url(*args, **kwargs):
    return AsyncMock()
redis.asyncio.from_url = mock_from_url
redis.asyncio.Redis.from_url = mock_from_url

import qdrant_client
mock_qdrant_class = MagicMock()
mock_qdrant_class.return_value.search = AsyncMock(return_value=[])
mock_qdrant_class.return_value.query_points = AsyncMock(return_value=MagicMock(points=[]))
qdrant_client.AsyncQdrantClient = mock_qdrant_class

import minio
minio.Minio = MagicMock()

# ── Environment variables (set BEFORE importing app) ────────────────────
import os
_test_env = {
    "DATABASE_URL":       "postgresql+asyncpg://test:test@localhost/test",
    "REDIS_URL":          "redis://localhost:6379",
    "USE_QDRANT":         "True",
    "QDRANT_URL":         "http://localhost:6333",
    "MINIO_URL":          "localhost:9000",
    "MINIO_ROOT_USER":    "minio",
    "MINIO_ROOT_PASSWORD":"minio123",
    "SECRET_KEY":         "super-secret",
    "DB_PASS":            "test",
    "LITELLM_URL":        "http://localhost:4000",
    "ENVIRONMENT":        "local",
}
for k, v in _test_env.items():
    os.environ.setdefault(k, v)
os.environ["USE_QDRANT"] = "True"

# ── Patch SQLAlchemy Uuid type for SQLite support ───────────────────────
#    Must patch BEFORE models are loaded so metadata.create_all uses CHAR(32).
from sqlalchemy.sql import sqltypes as _sqltypes
import sqlalchemy.types as _sa_types

_orig_gen_impl = _sqltypes.Uuid._gen_dialect_impl

def _sqlite_gen_dialect_impl(self, dialect):
    if dialect.name == "sqlite":
        return dialect.type_descriptor(_sa_types.CHAR(32))
    return _orig_gen_impl(self, dialect)

_sqltypes.Uuid._gen_dialect_impl = _sqlite_gen_dialect_impl

# Also patch bind_processor to handle both UUID objects and strings
_orig_bind = _sqltypes.Uuid.bind_processor

def _sqlite_bind_processor(self, dialect):
    if dialect.name == "sqlite":
        def process(value):
            if value is None:
                return value
            if isinstance(value, _uuid.UUID):
                return value.hex
            try:
                return _uuid.UUID(str(value)).hex
            except (ValueError, AttributeError):
                return str(value)
        return process
    return _orig_bind(self, dialect)

_sqltypes.Uuid.bind_processor = _sqlite_bind_processor

_orig_result = _sqltypes.Uuid.result_processor

def _sqlite_result_processor(self, dialect, coltype):
    if dialect.name == "sqlite":
        def process(value):
            if value is None:
                return value
            if isinstance(value, _uuid.UUID):
                return value
            try:
                return _uuid.UUID(value)
            except (ValueError, AttributeError):
                return value
        return process
    return _orig_result(self, dialect, coltype)

_sqltypes.Uuid.result_processor = _sqlite_result_processor

# ── NOW import app ──────────────────────────────────────────────────────
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

from sqlalchemy.pool import StaticPool

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

import app.db.session
app.db.session.AsyncSessionLocal = TestingSessionLocal
app.db.session.engine = engine

from app.db.base import Base
from app.main import app
from app.dependencies import get_db

app.state.limiter.enabled = False

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(autouse=True)
async def cleanup_db(db_session: AsyncSession):
    """Clear all tables before each test to ensure isolation with StaticPool."""
    from sqlalchemy import delete
    from app.db.models import (
        Tenant, User, Document, DocumentChunk, AgentRun, HITLApproval,
        AuditEvent, CostEvent, Conversation, Message, Lead, SystemSetting,
        ClientMemory, Project, Milestone, Invoice, PromptVersion, Approval
    )
    
    # Order: Children first to avoid FK violations
    tables = [
        Message, Conversation, DocumentChunk, Document,
        HITLApproval, AgentRun, AuditEvent, CostEvent,
        Milestone, Invoice, Project, Lead,
        ClientMemory, SystemSetting, PromptVersion, Approval,
        User, Tenant
    ]
    
    for table in tables:
        try:
            await db_session.execute(delete(table))
        except:
            pass
    await db_session.commit()

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    from app.db import qdrant_client as db_qdrant
    if db_qdrant.qdrant is None:
        mock_q = MagicMock()
        mock_q.search = AsyncMock(return_value=[])
        mock_q.query_points = AsyncMock(return_value=MagicMock(points=[]))
        db_qdrant.qdrant = mock_q

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()

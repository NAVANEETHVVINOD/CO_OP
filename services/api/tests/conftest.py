import sys
from unittest.mock import MagicMock, AsyncMock

# Overrides for models to avoid downloading from HF during tests
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

# Override for Redis to prevent Error 11001 connection faults during local testing
import redis.asyncio
def mock_from_url(*args, **kwargs):
    return AsyncMock()
redis.asyncio.from_url = mock_from_url
redis.asyncio.Redis.from_url = mock_from_url

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.db.base import Base
from app.main import app
from app.dependencies import get_db

app.state.limiter.enabled = False

# Use an in-memory SQLite database for testing, but since sqlalchemy async engine with
# sqlite requires aiosqlite, we use sqlite+aiosqlite:// url.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    # SQLite specific args:
    pool_recycle=3600,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()

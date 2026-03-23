import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


async def _check_postgres() -> str:
    try:
        from app.db.session import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as e:
        logger.error(f"Postgres health check failed: {e}")
        return "error"


async def _check_redis() -> str:
    try:
        from app.core.redis_client import redis_client
        result = await redis_client.ping()
        return "ok" if result else "error"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return "error"


async def _check_qdrant() -> str:
    try:
        import httpx
        from app.config import get_settings
        settings = get_settings()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.QDRANT_URL}/healthz", timeout=3.0)
            return "ok" if resp.status_code == 200 else "error"
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return "error"


async def _check_minio() -> str:
    try:
        from app.core.minio_client import minio_client
        minio_client.list_buckets()
        return "ok"
    except Exception as e:
        logger.error(f"MinIO health check failed: {e}")
        return "error"


# ─── Stage 2 health checks ─────────────────────────────────────────

async def _check_ollama() -> str:
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://ollama:11434/api/tags", timeout=5.0)
            return "ok" if resp.status_code == 200 else "error"
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        return "error"


async def _check_litellm() -> str:
    try:
        import httpx
        from app.config import get_settings
        settings = get_settings()
        if not settings.LITELLM_URL:
            return "not_configured"
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.LITELLM_URL}/health", timeout=5.0)
            return "ok" if resp.status_code == 200 else "error"
    except Exception as e:
        logger.error(f"LiteLLM health check failed: {e}")
        return "error"


@router.get("/health")
async def check_health():
    pg = await _check_postgres()
    rd = await _check_redis()
    qd = await _check_qdrant()
    mo = await _check_minio()
    ol = await _check_ollama()
    ll = await _check_litellm()
    return {
        "status": "ok",
        "postgres": pg,
        "redis": rd,
        "qdrant": qd,
        "minio": mo,
        "ollama": ol,
        "litellm": ll,
    }


@router.get("/ready")
async def readiness_check():
    pg = await _check_postgres()
    rd = await _check_redis()
    qd = await _check_qdrant()
    mo = await _check_minio()
    ol = await _check_ollama()
    ll = await _check_litellm()
    # Core services (Stage 1) must be healthy; Stage 2 services are optional
    core_ok = pg == "ok" and rd == "ok" and qd == "ok" and mo == "ok"
    status_code = 200 if core_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if core_ok else "degraded",
            "postgres": pg,
            "redis": rd,
            "qdrant": qd,
            "minio": mo,
            "ollama": ol,
            "litellm": ll,
        },
    )

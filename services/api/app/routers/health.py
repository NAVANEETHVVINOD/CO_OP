import logging
import time
from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


async def _check_service_with_latency(check_func, service_name: str) -> Dict[str, Any]:
    """Execute a health check and measure latency"""
    start_time = time.time()
    try:
        status = await check_func()
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "status": status,
            "healthy": status == "ok",
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"{service_name} health check failed: {e}")
        return {
            "status": "error",
            "healthy": False,
            "latency_ms": latency_ms,
            "error": str(e)
        }


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
        from app.config import get_settings
        settings = get_settings()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.OLLAMA_URL}/api/tags", timeout=5.0)
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
    from app.config import get_settings
    settings = get_settings()
    
    # Check all services with latency measurements
    pg = await _check_service_with_latency(_check_postgres, "postgres")
    rd = await _check_service_with_latency(_check_redis, "redis")
    qd = await _check_service_with_latency(_check_qdrant, "qdrant")
    mo = await _check_service_with_latency(_check_minio, "minio")
    ol = await _check_service_with_latency(_check_ollama, "ollama")
    ll = await _check_service_with_latency(_check_litellm, "litellm")
    
    # Determine overall status
    core_services = [pg, rd, qd, mo]
    all_core_healthy = all(svc["healthy"] for svc in core_services)
    overall_status = "ok" if all_core_healthy else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.3",
        "environment": settings.ENVIRONMENT,
        "simulation_mode": settings.COOP_SIMULATION_MODE,
        "services": {
            "postgres": pg,
            "redis": rd,
            "qdrant": qd,
            "minio": mo,
            "ollama": ol,
            "litellm": ll
        }
    }


@router.get("/ready")
async def readiness_check():
    # Check all services with latency
    pg = await _check_service_with_latency(_check_postgres, "postgres")
    rd = await _check_service_with_latency(_check_redis, "redis")
    qd = await _check_service_with_latency(_check_qdrant, "qdrant")
    mo = await _check_service_with_latency(_check_minio, "minio")
    ol = await _check_service_with_latency(_check_ollama, "ollama")
    ll = await _check_service_with_latency(_check_litellm, "litellm")
    
    # Core services (Stage 1) must be healthy; Stage 2 services are optional
    core_ok = pg["healthy"] and rd["healthy"] and qd["healthy"] and mo["healthy"]
    status_code = 200 if core_ok else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if core_ok else "not_ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "postgres": pg,
                "redis": rd,
                "qdrant": qd,
                "minio": mo,
                "ollama": ol,
                "litellm": ll
            }
        },
    )

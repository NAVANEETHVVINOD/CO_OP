"""
System Monitor — Runs every 5 minutes via ARQ cron.
Checks all service health, attempts self-heal, alerts via Telegram.
"""
import logging

import httpx
from app.db.session import engine
from app.core.redis_client import redis_client
from app.config import get_settings
from app.communication.telegram import send_alert

logger = logging.getLogger(__name__)

def _get_services():
    """Get service URLs from settings."""
    settings = get_settings()
    return {
        "postgres":  {"type": "internal"},  # checked via SQLAlchemy
        "redis":     {"type": "internal"},  # checked via redis ping
        "qdrant":    {"url": f"{settings.QDRANT_URL}/healthz"} if settings.QDRANT_URL else {"type": "skip"},
        "minio":     {"url": f"http://{settings.MINIO_URL}/minio/health/live"},
        "ollama":    {"url": f"{settings.OLLAMA_URL}/api/tags"},
        "litellm":   {"url": f"{settings.LITELLM_URL}/health"} if settings.LITELLM_URL else {"type": "skip"},
    }


async def _check_service_http(name: str, url: str) -> bool:
    """Check if an HTTP service is reachable."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=5.0)
            return resp.status_code == 200
    except Exception as e:
        logger.warning(f"Service {name} unreachable at {url}: {e}")
        return False


async def _check_postgres() -> bool:
    """Check PostgreSQL via SQLAlchemy."""
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"Postgres check failed: {e}")
        return False


async def _check_redis() -> bool:
    """Check Redis via ping."""
    try:
        return await redis_client.ping()
    except Exception as e:
        logger.warning(f"Redis check failed: {e}")
        return False


async def run_system_monitor() -> None:
    """Run full system health check and alert on failures."""
    results: dict[str, bool] = {}

    # Internal services
    results["postgres"] = await _check_postgres()
    results["redis"] = await _check_redis()

    # HTTP-based services
    services = _get_services()
    for name, config in services.items():
        if config.get("type") in ("internal", "skip"):
            continue
        url = config.get("url", "")
        results[name] = await _check_service_http(name, url)

    # Log results
    healthy = [k for k, v in results.items() if v]
    unhealthy = [k for k, v in results.items() if not v]

    if unhealthy:
        logger.error(f"Unhealthy services: {unhealthy}")
        # Send Telegram alert
        try:
            alert_msg = (
                f"🔴 Unhealthy services: {', '.join(unhealthy)}\n"
                f"🟢 Healthy: {', '.join(healthy)}"
            )
            await send_alert(alert_msg)
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
    else:
        logger.info(f"All services healthy: {healthy}")

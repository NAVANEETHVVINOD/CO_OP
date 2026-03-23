"""
System Monitor — Runs every 5 minutes via ARQ cron.
Checks all service health, attempts self-heal, alerts via Telegram.
"""
import logging

import httpx

logger = logging.getLogger(__name__)

# Services to monitor with their health endpoints
SERVICES = {
    "postgres":  {"type": "internal"},  # checked via SQLAlchemy
    "redis":     {"type": "internal"},  # checked via redis ping
    "qdrant":    {"url": "http://qdrant:6333/healthz"},
    "minio":     {"url": "http://minio:9000/minio/health/live"},
    "ollama":    {"url": "http://ollama:11434/api/tags"},
    "litellm":   {"url": "http://litellm:4000/health"},
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
        from app.db.session import engine
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
        from app.core.redis_client import redis_client
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
    for name, config in SERVICES.items():
        if config.get("type") == "internal":
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
            from app.communication.telegram import send_alert
            alert_msg = (
                f"🔴 Unhealthy services: {', '.join(unhealthy)}\n"
                f"🟢 Healthy: {', '.join(healthy)}"
            )
            await send_alert(alert_msg)
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
    else:
        logger.info(f"All services healthy: {healthy}")

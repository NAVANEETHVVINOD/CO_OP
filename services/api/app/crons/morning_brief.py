"""
Morning Brief — Runs daily at 8am via ARQ cron.
Gathers: new leads, system health, token usage. Sends summary via Telegram.
"""
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func

logger = logging.getLogger(__name__)


async def run_morning_brief() -> None:
    """Gather daily summary and send via Telegram."""
    logger.info("Generating morning brief...")

    lines = ["☀️ *Co-Op Morning Brief*\n"]
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(hours=24)

    # 1. New leads in last 24h
    try:
        from app.db.session import AsyncSessionLocal
        from app.db.models import Lead

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(func.count(Lead.id)).where(Lead.found_at >= yesterday)
            )
            lead_count = result.scalar() or 0
        lines.append(f"🎯 *New Leads*: {lead_count} found in last 24h")
    except Exception as e:
        logger.warning(f"Failed to count leads: {e}")
        lines.append("🎯 *New Leads*: unavailable")

    # 2. System health
    try:
        import httpx
        from app.config import get_settings
        settings = get_settings()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.API_BASE_URL}/health", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                healthy = sum(1 for k, v in data.items() if k != "status" and v == "ok")
                total = sum(1 for k in data if k != "status")
                lines.append(f"🏥 *System Health*: {healthy}/{total} services OK")
            else:
                lines.append("🏥 *System Health*: check failed")
    except Exception as e:
        logger.warning(f"Failed health check: {e}")
        lines.append("🏥 *System Health*: unavailable")

    # 3. Token usage (last 24h)
    try:
        from app.db.session import AsyncSessionLocal
        from app.db.models import CostEvent

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(
                    func.sum(CostEvent.prompt_tokens + CostEvent.completion_tokens),
                    func.sum(CostEvent.cost),
                ).where(CostEvent.created_at >= yesterday)
            )
            row = result.first()
            total_tokens = row[0] or 0
            total_cost = row[1] or 0.0
        lines.append(f"💰 *Token Usage*: {total_tokens:,} tokens (${total_cost:.4f})")
    except Exception as e:
        logger.warning(f"Failed to get token usage: {e}")
        lines.append("💰 *Token Usage*: unavailable")

    lines.append(f"\n_Report generated at {now.strftime('%H:%M UTC')}_")

    # Send via Telegram
    brief = "\n".join(lines)
    try:
        from app.communication.telegram import send_message
        await send_message(brief)
        logger.info("Morning brief sent to Telegram.")
    except Exception as e:
        logger.error(f"Failed to send morning brief: {e}")

    # Also log it
    logger.info(f"Morning brief:\n{brief}")

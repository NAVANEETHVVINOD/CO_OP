import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Milestone

logger = logging.getLogger(__name__)

async def track_deadlines(db: AsyncSession):
    """
    Agent: Project Tracker (Cron-style).
    Scans for milestones due within 72 hours and active projects with no updates.
    """
    now = datetime.now(timezone.utc)
    threshold = now + timedelta(hours=72)
    
    # 1. Approaching Milestones
    stmt = select(Milestone).where(
        Milestone.status == "pending",
        Milestone.due_date <= threshold
    )
    result = await db.execute(stmt)
    upcoming = result.scalars().all()
    
    for ms in upcoming:
        logger.warning(f"[TRACKER] Milestone deadline warning: '{ms.title}' is due on {ms.due_date}")
        # In actual Stage 3, this would push a notification to Telegram.

    # 2. Stale Projects (No activity > 7 days)
    # (Implementation for Phase 4)
    
    return {"milestones_flagged": len(upcoming)}

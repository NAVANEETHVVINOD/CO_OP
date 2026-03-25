import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Lead, Project

logger = logging.getLogger(__name__)

async def compute_performance_stats(db: AsyncSession):
    """
    Agent: Self-Improvement Analyst.
    Scans the database for success trends and calculates KPIs like:
    - Outreach conversion rate
    - Average lead score vs success
    """
    logger.info("Self-Improvement: Analyzing success performance...")
    
    # 1. Conversion Rate
    applied_count = await db.scalar(select(func.count(Lead.id)).where(Lead.status == "applied"))
    converted_count = await db.scalar(select(func.count(Project.id)).where(Project.lead_id != None))
    
    rate = (converted_count / applied_count) if applied_count and applied_count > 0 else 0.0
    
    logger.info(f"[ANALYST] Conversion rate: {rate:.1%}")
    
    return {
        "conversion_rate": rate,
        "applied_count": applied_count,
        "converted_count": converted_count
    }

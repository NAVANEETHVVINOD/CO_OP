"""Credits router — Token usage endpoint for dashboard widget."""
import logging
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import verify_token
from app.db.models import User, CostEvent

router = APIRouter(prefix="/v1/costs", tags=["Credits"])
logger = logging.getLogger(__name__)

DAILY_TOKEN_LIMIT = 100_000  # Default daily token budget


@router.get("")
async def get_credit_usage(
    current_user: User = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Return today's and overall token usage for the dashboard widget."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Today's usage
    today_result = await db.execute(
        select(
            func.coalesce(func.sum(CostEvent.prompt_tokens), 0),
            func.coalesce(func.sum(CostEvent.completion_tokens), 0),
            func.coalesce(func.sum(CostEvent.cost), 0.0),
        ).where(CostEvent.created_at >= today_start)
    )
    today_row = today_result.first()
    today_prompt = today_row[0] if today_row else 0
    today_completion = today_row[1] if today_row else 0
    today_cost = today_row[2] if today_row else 0.0
    today_total = today_prompt + today_completion

    # All-time usage
    total_result = await db.execute(
        select(
            func.coalesce(func.sum(CostEvent.prompt_tokens), 0),
            func.coalesce(func.sum(CostEvent.completion_tokens), 0),
            func.coalesce(func.sum(CostEvent.cost), 0.0),
        )
    )
    total_row = total_result.first()
    total_prompt = total_row[0] if total_row else 0
    total_completion = total_row[1] if total_row else 0
    total_cost = total_row[2] if total_row else 0.0

    usage_pct = min(100.0, (today_total / DAILY_TOKEN_LIMIT) * 100) if DAILY_TOKEN_LIMIT > 0 else 0

    return {
        "today": {
            "prompt_tokens": today_prompt,
            "completion_tokens": today_completion,
            "total_tokens": today_total,
            "total_cost": round(today_cost, 6),
            "usage_pct": round(usage_pct, 1),
        },
        "all_time": {
            "prompt_tokens": total_prompt,
            "completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
            "total_cost": round(total_cost, 6),
        },
        "daily_limit": DAILY_TOKEN_LIMIT,
    }

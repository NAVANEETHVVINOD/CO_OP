"""Settings router — Hardware tier and system settings endpoint."""
import logging

from fastapi import APIRouter
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import SystemSetting

router = APIRouter(prefix="/v1/settings", tags=["Settings"])
logger = logging.getLogger(__name__)


@router.get("/hardware")
async def get_hardware_tier():
    """Return the detected hardware tier and system info."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(SystemSetting).where(SystemSetting.key == "hardware_tier")
            )
            setting = result.scalars().first()
            if setting:
                return setting.value
    except Exception as e:
        logger.error(f"Failed to read hardware tier: {e}")

    # Fallback: run detection now
    try:
        from app.core.hardware_detector import detect_hardware, assign_tier
        hw = detect_hardware()
        tier = assign_tier(hw)
        return {"tier": tier, **hw}
    except Exception as e:
        logger.error(f"Hardware detection failed: {e}")
        return {"tier": "UNKNOWN", "error": str(e)}

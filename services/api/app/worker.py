"""
ARQ Worker — Background task runner for Co-Op.
Runs as a separate process alongside the FastAPI server (via supervisord).
"""
import logging
from arq import cron
from arq.connections import RedisSettings

from app.config import get_settings

logger = logging.getLogger(__name__)


# ─── Task Functions ─────────────────────────────────────────────────

async def system_monitor_task(ctx: dict) -> None:
    """Check all services every 5 minutes. Alert via Telegram on failure."""
    logger.info("Running system monitor...")
    from app.crons.system_monitor import run_system_monitor
    await run_system_monitor()


async def lead_scout_task(ctx: dict) -> None:
    """Search for matching Upwork jobs every 4 hours."""
    logger.info("Running lead scout...")
    from app.agent.lead_scout import run_lead_scout
    await run_lead_scout()


async def morning_brief_task(ctx: dict) -> None:
    """Send daily morning brief via Telegram at 8am."""
    logger.info("Running morning brief...")
    from app.crons.morning_brief import run_morning_brief
    await run_morning_brief()


async def project_tracking_task(ctx: dict) -> None:
    """Check milestones and project health every 24 hours."""
    logger.info("Running project tracker...")
    from app.agent.project_tracker import track_deadlines
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await track_deadlines(db)


async def finance_manager_task(ctx: dict) -> None:
    """Scan for billable milestones and handle payments every 24 hours."""
    logger.info("Running finance manager...")
    from app.agent.finance_manager import process_billing
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await process_billing(db)


# ─── Worker Settings ────────────────────────────────────────────────

def _get_redis_settings() -> RedisSettings:
    settings = get_settings()
    redis_url = settings.REDIS_URL
    # Parse redis://host:port/db
    if redis_url.startswith("redis://"):
        parts = redis_url.replace("redis://", "").split("/")
        host_port = parts[0]
        database = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        host, port = host_port.split(":") if ":" in host_port else (host_port, 6379)
        return RedisSettings(host=str(host), port=int(port), database=database)
    return RedisSettings()


class WorkerSettings:
    """ARQ worker configuration."""
    functions = [
        system_monitor_task, 
        lead_scout_task, 
        morning_brief_task,
        project_tracking_task,
        finance_manager_task
    ]
    redis_settings = _get_redis_settings()

    cron_jobs = [
        # System monitor: every 5 minutes
        cron(
            system_monitor_task,
            minute={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55},
        ),
        # Lead scout: every 4 hours at minute 30
        cron(
            lead_scout_task,
            hour={2, 6, 10, 14, 18, 22},
            minute={30},
        ),
        # Morning brief: daily at 08:00 UTC
        cron(
            morning_brief_task,
            hour={8},
            minute={0},
        ),
        # Project Tracking: daily at 00:00 UTC
        cron(
            project_tracking_task,
            hour={0},
            minute={0},
        ),
        # Finance Manager: daily at 01:00 UTC
        cron(
            finance_manager_task,
            hour={1},
            minute={0},
        ),
    ]

    # Worker behavior
    max_jobs = 5
    job_timeout = 300  # 5 minutes max per job
    allow_abort_jobs = True

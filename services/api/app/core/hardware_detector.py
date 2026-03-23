"""
Hardware Detector — Determines system capabilities and assigns a tier.
Uses psutil for RAM/CPU and optionally detects GPU availability.

Tiers:
  - SOLO:   ≤8GB RAM   → use 3B models only
  - TEAM:   ≤16GB RAM  → use 3B + 8B models
  - AGENCY: >16GB RAM  → use all models + cloud overflow
"""
import logging
from typing import Dict, Any

import psutil

logger = logging.getLogger(__name__)


def detect_hardware() -> Dict[str, Any]:
    """Detect system hardware and return capabilities dict."""
    ram_bytes = psutil.virtual_memory().total
    ram_gb = round(ram_bytes / (1024 ** 3), 1)
    cpu_cores = psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True) or 1
    cpu_threads = psutil.cpu_count(logical=True) or 1

    # Try to detect CPU model
    cpu_model = "Unknown"
    try:
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        cpu_model = info.get("brand_raw", "Unknown")
    except Exception:
        pass

    # GPU detection (best effort)
    gpu_available = False
    gpu_name = None
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            gpu_available = True
            gpu_name = result.stdout.strip().split("\n")[0]
    except Exception:
        pass

    return {
        "ram_gb": ram_gb,
        "cpu_cores": cpu_cores,
        "cpu_threads": cpu_threads,
        "cpu_model": cpu_model,
        "gpu_available": gpu_available,
        "gpu_name": gpu_name,
    }


def assign_tier(hardware: Dict[str, Any]) -> str:
    """Assign a tier based on hardware capabilities."""
    ram_gb = hardware.get("ram_gb", 0)
    if ram_gb <= 8:
        return "SOLO"
    elif ram_gb <= 16:
        return "TEAM"
    else:
        return "AGENCY"


async def detect_and_store_hardware() -> Dict[str, Any]:
    """Detect hardware, assign tier, and store in SystemSetting table."""
    hardware = detect_hardware()
    tier = assign_tier(hardware)

    result = {
        "tier": tier,
        **hardware,
    }

    logger.info(f"Hardware detected: {hardware['ram_gb']}GB RAM, {hardware['cpu_cores']} cores, "
                f"GPU: {hardware['gpu_name'] or 'None'} → Tier: {tier}")

    # Store in database
    try:
        from app.db.session import AsyncSessionLocal
        from app.db.models import SystemSetting
        from sqlalchemy import select

        async with AsyncSessionLocal() as session:
            existing = await session.execute(
                select(SystemSetting).where(SystemSetting.key == "hardware_tier")
            )
            setting = existing.scalars().first()
            if setting:
                setting.value = result
            else:
                setting = SystemSetting(key="hardware_tier", value=result)
                session.add(setting)
            await session.commit()
        logger.info(f"Hardware tier '{tier}' stored in database.")
    except Exception as e:
        logger.error(f"Failed to store hardware tier: {e}")

    return result

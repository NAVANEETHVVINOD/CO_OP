"""Enhanced tests for settings router."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import SystemSetting


@pytest.mark.asyncio
async def test_get_hardware_tier_no_setting(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/settings/hardware returns hardware tier (fallback to detection)."""
    response = await async_client.get("/v1/settings/hardware")
    assert response.status_code == 200
    data = response.json()
    assert "tier" in data
    # Should have detected hardware tier (SOLO, TEAM, or AGENCY)
    assert data["tier"] in ["SOLO", "TEAM", "AGENCY"]


@pytest.mark.asyncio
async def test_get_hardware_tier_with_setting(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/settings/hardware returns stored hardware tier."""
    # Store a hardware tier setting
    setting = SystemSetting(
        key="hardware_tier",
        value={
            "tier": "AGENCY",
            "cpu_count": 8,
            "ram_gb": 16,
            "gpu_available": True
        }
    )
    db_session.add(setting)
    await db_session.commit()
    
    response = await async_client.get("/v1/settings/hardware")
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "AGENCY"
    assert data["cpu_count"] == 8
    assert data["ram_gb"] == 16


@pytest.mark.asyncio
async def test_get_hardware_tier_low(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/settings/hardware returns SOLO tier for low-spec hardware."""
    setting = SystemSetting(
        key="hardware_tier",
        value={
            "tier": "SOLO",
            "cpu_count": 2,
            "ram_gb": 4,
            "gpu_available": False
        }
    )
    db_session.add(setting)
    await db_session.commit()
    
    response = await async_client.get("/v1/settings/hardware")
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "SOLO"
    assert data["gpu_available"] is False


@pytest.mark.asyncio
async def test_get_hardware_tier_medium(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/settings/hardware returns TEAM tier."""
    setting = SystemSetting(
        key="hardware_tier",
        value={
            "tier": "TEAM",
            "cpu_count": 4,
            "ram_gb": 8,
            "gpu_available": False
        }
    )
    db_session.add(setting)
    await db_session.commit()
    
    response = await async_client.get("/v1/settings/hardware")
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "TEAM"

import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_get_settings_hardware(async_client: AsyncClient):
    with patch("app.routers.settings.detect_startup_hardware_tier") as mock_detect:
        mock_detect.return_value = "TEAM"
        
        response = await async_client.get("/v1/settings/hardware")
        assert response.status_code == 200
        
        data = response.json()
        assert data["tier"] in ["SOLO", "TEAM", "AGENCY"]

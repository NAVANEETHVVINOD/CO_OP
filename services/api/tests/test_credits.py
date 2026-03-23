import pytest
from httpx import AsyncClient
from app.main import app
from app.dependencies import verify_token

from app.db.models import User

@pytest.mark.asyncio
async def test_get_costs(async_client: AsyncClient):
    dummy_user = User(id="test-uid", email="test@test.com")
    app.dependency_overrides[verify_token] = lambda: dummy_user

    # This also tests that the endpoint doesn't crash if cost_events table is empty
    response = await async_client.get("/v1/costs")
    
    app.dependency_overrides.pop(verify_token, None)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "today" in data
    assert "all_time" in data
    assert "daily_limit" in data
    
    # Defaults
    assert data["today"]["total_cost"] == 0.0
    assert data["all_time"]["total_cost"] == 0.0

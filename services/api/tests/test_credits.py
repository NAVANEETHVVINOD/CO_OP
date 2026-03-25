import pytest
from httpx import AsyncClient
from datetime import datetime, timezone

from app.main import app
from app.dependencies import verify_token
from app.db.models import User, CostEvent

@pytest.mark.asyncio
async def test_get_costs_with_data(async_client: AsyncClient, db_session):
    dummy_user = User(id="test-uid", email="test@test.com")
    app.dependency_overrides[verify_token] = lambda: dummy_user

    import uuid
    tenant_uuid = uuid.uuid4()
    # Add dummy cost events
    # One for today
    today_event = CostEvent(tenant_id=tenant_uuid, model_name="litellm", cost=2.50, prompt_tokens=500, completion_tokens=500)
    db_session.add(today_event)
    
    # One for yesterday
    past_event = CostEvent(tenant_id=tenant_uuid, model_name="litellm", cost=1.50, prompt_tokens=250, completion_tokens=250)
    # The default created_at is datetime.now(timezone.utc), but we'll manually set it for the past_event
    past_event.created_at = datetime(2023, 1, 1, tzinfo=timezone.utc)
    db_session.add(past_event)
    
    await db_session.commit()

    response = await async_client.get("/v1/costs")
    
    app.dependency_overrides.pop(verify_token, None)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "today" in data
    assert "all_time" in data
    assert data["today"]["total_cost"] == 2.50
    assert data["all_time"]["total_cost"] == 4.00

"""Enhanced tests for credits/costs router."""
import pytest
import uuid
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.v1_test_utils import seed_test_user
from app.db.models import CostEvent


@pytest.mark.asyncio
async def test_get_costs_without_usage(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/costs should return zero costs when no usage."""
    user, token = await seed_test_user(db_session)
    
    response = await async_client.get(
        "/v1/costs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["today"]["total_tokens"] == 0
    assert data["today"]["total_cost"] == 0.0
    assert data["all_time"]["total_tokens"] == 0
    assert data["all_time"]["total_cost"] == 0.0


@pytest.mark.asyncio
async def test_get_costs_with_today_usage(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/costs reflects costs from today's usage."""
    user, token = await seed_test_user(db_session)
    
    # Add a cost event for today
    cost_event = CostEvent(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        model_name="test-model",
        prompt_tokens=100,
        completion_tokens=50,
        cost=0.0015,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(cost_event)
    await db_session.commit()
    
    response = await async_client.get(
        "/v1/costs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["today"]["prompt_tokens"] == 100
    assert data["today"]["completion_tokens"] == 50
    assert data["today"]["total_tokens"] == 150
    assert data["today"]["total_cost"] == 0.0015
    assert data["all_time"]["total_tokens"] == 150


@pytest.mark.asyncio
async def test_get_costs_with_historical_usage(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/costs separates today's usage from historical."""
    user, token = await seed_test_user(db_session)
    
    # Add a cost event from yesterday
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    old_event = CostEvent(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        model_name="test-model",
        prompt_tokens=200,
        completion_tokens=100,
        cost=0.003,
        created_at=yesterday
    )
    db_session.add(old_event)
    
    # Add a cost event for today
    today_event = CostEvent(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        model_name="test-model",
        prompt_tokens=50,
        completion_tokens=25,
        cost=0.00075,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(today_event)
    await db_session.commit()
    
    response = await async_client.get(
        "/v1/costs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Today should only have today's event
    assert data["today"]["total_tokens"] == 75
    assert data["today"]["total_cost"] == 0.00075
    
    # All-time should have both
    assert data["all_time"]["total_tokens"] == 375
    assert data["all_time"]["total_cost"] == 0.00375


@pytest.mark.asyncio
async def test_get_costs_usage_percentage(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/costs calculates usage percentage correctly."""
    user, token = await seed_test_user(db_session)
    
    # Add cost event with 10,000 tokens (10% of 100,000 daily limit)
    cost_event = CostEvent(
        id=uuid.uuid4(),
        tenant_id=user.tenant_id,
        model_name="test-model",
        prompt_tokens=7000,
        completion_tokens=3000,
        cost=0.01,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(cost_event)
    await db_session.commit()
    
    response = await async_client.get(
        "/v1/costs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["today"]["usage_pct"] == 10.0
    assert data["daily_limit"] == 100_000


@pytest.mark.asyncio
async def test_get_costs_multiple_events(async_client: AsyncClient, db_session: AsyncSession):
    """GET /v1/costs aggregates multiple cost events."""
    user, token = await seed_test_user(db_session)
    
    # Add multiple cost events for today
    for i in range(5):
        cost_event = CostEvent(
            id=uuid.uuid4(),
            tenant_id=user.tenant_id,
            model_name="test-model",
            prompt_tokens=100,
            completion_tokens=50,
            cost=0.0015,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(cost_event)
    await db_session.commit()
    
    response = await async_client.get(
        "/v1/costs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["today"]["prompt_tokens"] == 500
    assert data["today"]["completion_tokens"] == 250
    assert data["today"]["total_tokens"] == 750
    assert data["today"]["total_cost"] == 0.0075

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Approval
from tests.v1_test_utils import seed_test_user


@pytest.mark.asyncio
async def test_approvals_list(async_client: AsyncClient, db_session: AsyncSession, mocker):
    """Test listing all approvals"""
    user, token = await seed_test_user(db_session)
    mocker.patch("app.agent.outreach_manager.submit_outreach")

    # Create multiple approvals
    approval1 = Approval(
        tenant_id=user.tenant_id,
        entity_type="proposal",
        entity_id=uuid.uuid4(),
        data={"message": "test outreach 1"},
        status="pending"
    )
    approval2 = Approval(
        tenant_id=user.tenant_id,
        entity_type="invoice",
        entity_id=uuid.uuid4(),
        data={"amount": 1000},
        status="pending"
    )
    db_session.add_all([approval1, approval2])
    await db_session.commit()

    # List Approvals
    list_resp = await async_client.get(
        "/v1/approvals",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_resp.status_code == 200
    approvals = list_resp.json()
    assert len(approvals) >= 2


@pytest.mark.asyncio
async def test_approvals_approve_action(async_client: AsyncClient, db_session: AsyncSession, mocker):
    """Test approving a pending approval"""
    user, token = await seed_test_user(db_session)
    mocker.patch("app.agent.outreach_manager.submit_outreach")

    approval = Approval(
        tenant_id=user.tenant_id,
        entity_type="proposal",
        entity_id=uuid.uuid4(),
        data={"message": "test outreach"},
        status="pending"
    )
    db_session.add(approval)
    await db_session.commit()

    # Approve Action
    app_resp = await async_client.post(
        f"/v1/approvals/{approval.id}/approve",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert app_resp.status_code == 200

    # Verify Status
    await db_session.refresh(approval)
    assert approval.status == "approved"


@pytest.mark.asyncio
async def test_approvals_reject_action(async_client: AsyncClient, db_session: AsyncSession):
    """Test rejecting a pending approval"""
    user, token = await seed_test_user(db_session)

    approval = Approval(
        tenant_id=user.tenant_id,
        entity_type="invoice",
        entity_id=uuid.uuid4(),
        status="pending"
    )
    db_session.add(approval)
    await db_session.commit()

    # Reject Action
    rej_resp = await async_client.post(
        f"/v1/approvals/{approval.id}/reject",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert rej_resp.status_code == 200
    await db_session.refresh(approval)
    assert approval.status == "rejected"


@pytest.mark.asyncio
async def test_approvals_nonexistent(async_client: AsyncClient, db_session: AsyncSession):
    """Test approving non-existent approval"""
    user, token = await seed_test_user(db_session)
    
    fake_id = uuid.uuid4()
    response = await async_client.post(
        f"/v1/approvals/{fake_id}/approve",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_approvals_without_auth(async_client: AsyncClient):
    """Test accessing approvals without authentication"""
    response = await async_client.get("/v1/approvals")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_approvals_double_approve(async_client: AsyncClient, db_session: AsyncSession, mocker):
    """Test approving an already approved approval"""
    user, token = await seed_test_user(db_session)
    mocker.patch("app.agent.outreach_manager.submit_outreach")

    approval = Approval(
        tenant_id=user.tenant_id,
        entity_type="proposal",
        entity_id=uuid.uuid4(),
        data={"message": "test"},
        status="approved"  # Already approved
    )
    db_session.add(approval)
    await db_session.commit()

    # Try to approve again
    response = await async_client.post(
        f"/v1/approvals/{approval.id}/approve",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should either succeed idempotently or return error
    assert response.status_code in [200, 400, 409]


@pytest.mark.asyncio
async def test_approvals_flow(async_client: AsyncClient, db_session, mocker):
    """Test complete HITL approval workflow"""
    user, token = await seed_test_user(db_session)

    # Mock outreach submission to avoid side effects
    mocker.patch("app.agent.outreach_manager.submit_outreach")

    approval = Approval(
        tenant_id=user.tenant_id,
        entity_type="proposal",
        entity_id=uuid.uuid4(),
        data={"message": "test outreach"},
        status="pending"
    )
    db_session.add(approval)
    await db_session.commit()

    # 1. List Approvals
    list_resp = await async_client.get(
        "/v1/approvals",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # 2. Approve Action
    app_resp = await async_client.post(
        f"/v1/approvals/{approval.id}/approve",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert app_resp.status_code == 200

    # Verify Status
    await db_session.refresh(approval)
    assert approval.status == "approved"

    # 3. Reject Action (Re-seed with all required fields)
    app2 = Approval(
        tenant_id=user.tenant_id,
        entity_type="invoice",
        entity_id=uuid.uuid4(),
        status="pending"
    )
    db_session.add(app2)
    await db_session.commit()

    rej_resp = await async_client.post(
        f"/v1/approvals/{app2.id}/reject",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert rej_resp.status_code == 200
    await db_session.refresh(app2)
    assert app2.status == "rejected"

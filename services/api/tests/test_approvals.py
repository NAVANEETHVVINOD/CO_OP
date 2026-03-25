import uuid
import pytest
from httpx import AsyncClient
from app.db.models import Approval
from tests.v1_test_utils import seed_test_user

@pytest.mark.asyncio
async def test_approvals_flow(async_client: AsyncClient, db_session, mocker):
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

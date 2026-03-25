import pytest
from httpx import AsyncClient
from app.db.models import Invoice, Project
from tests.v1_test_utils import seed_test_user

@pytest.mark.asyncio
async def test_list_invoices(async_client: AsyncClient, db_session):
    user, token = await seed_test_user(db_session)

    # Seed a project first (Invoice requires project_id FK)
    project = Project(
        tenant_id=user.tenant_id,
        title="Invoice Test Project",
        status="active"
    )
    db_session.add(project)
    await db_session.flush()

    invoice = Invoice(
        tenant_id=user.tenant_id,
        project_id=project.id,
        amount=500.0,
        currency="USD",
        status="pending"
    )
    db_session.add(invoice)
    await db_session.commit()

    response = await async_client.get(
        "/v1/invoices",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["amount"] == 500.0
    assert data[0]["project_id"] == str(project.id)

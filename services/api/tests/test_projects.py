import pytest
from httpx import AsyncClient
from app.db.models import Project, Milestone
from tests.v1_test_utils import seed_test_user

@pytest.mark.asyncio
async def test_list_projects(async_client: AsyncClient, db_session):
    user, token = await seed_test_user(db_session)
    
    # Create a project
    project = Project(
        tenant_id=user.tenant_id,
        title="Test Project",
        status="active"
    )
    db_session.add(project)
    await db_session.commit()
    
    response = await async_client.get(
        "/v1/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Project"

@pytest.mark.asyncio
async def test_milestone_completion(async_client: AsyncClient, db_session):
    user, token = await seed_test_user(db_session)
    
    project = Project(tenant_id=user.tenant_id, title="P1")
    db_session.add(project)
    await db_session.flush()
    
    milestone = Milestone(project_id=project.id, title="M1", description="M1", status="pending")
    db_session.add(milestone)
    await db_session.commit()
    
    # Complete milestone
    response = await async_client.post(
        f"/v1/projects/milestones/{milestone.id}/complete",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify in DB
    await db_session.refresh(milestone)
    assert milestone.status == "completed"

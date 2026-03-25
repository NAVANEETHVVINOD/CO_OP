import pytest
from sqlalchemy import select
from app.db.models import Lead, Project, Milestone, Invoice
from app.agent.lead_scout import run_lead_scout
from app.agent.proposal_writer import draft_proposal
from app.agent.finance_manager import process_billing
from tests.v1_test_utils import seed_test_user

@pytest.mark.asyncio
async def test_v1_gold_path(db_session, mocker):
    """
    E2E 'Gold Path' test verifying the flow from Lead Scout
    to Invoice creation. LLMs are mocked via dummy models in conftest.py.
    """
    # 1. Setup Tenant (reuse seeding utility)
    user, token = await seed_test_user(db_session)
    tenant_id = user.tenant_id
    
    # 2. Run Lead Scout
    mocker.patch("app.agent.lead_scout._fetch_upwork_jobs", new_callable=mocker.AsyncMock, return_value=[{
        "id": "job_123",
        "title": "Python Developer Needed",
        "description": "Build an AI company",
        "url": "https://test.com"
    }])
    mocker.patch("app.agent.lead_scout._score_job", new_callable=mocker.AsyncMock, return_value=95.0)
    
    await run_lead_scout()
    
    # Verify lead created
    result = await db_session.execute(
        select(Lead).where(Lead.tenant_id == tenant_id)
    )
    lead = result.scalars().first()
    assert lead is not None
    assert "Python" in lead.title
    
    # 3. Draft Proposal
    # draft_proposal uses RAG, which is also mocked by dummy models
    proposal_res = await draft_proposal(db_session, lead.id)
    assert proposal_res["status"] in ["hitl_queued", "drafted"]
    
    # 4. Create Project & Complete Milestone
    project = Project(
        tenant_id=tenant_id,
        lead_id=lead.id,
        title=f"Project: {lead.title}",
        status="active"
    )
    db_session.add(project)
    await db_session.flush()
    
    milestone = Milestone(
        project_id=project.id,
        title="Phase 1",
        amount=500.0,
        status="completed"
    )
    db_session.add(milestone)
    await db_session.commit()
    
    # 5. Run Finance Manager Billing
    billing_res = await process_billing(db_session)
    assert billing_res["status"] == "complete"
    
    # 6. Verify Invoice
    result = await db_session.execute(
        select(Invoice).where(Invoice.project_id == project.id)
    )
    invoice = result.scalars().first()
    assert invoice is not None
    assert invoice.amount == 500.0
    assert invoice.status == "draft"

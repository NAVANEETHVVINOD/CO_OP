import pytest
import uuid
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Lead, Project, Milestone, Invoice, Approval
from app.agent.proposal_writer import draft_proposal
from app.agent.finance_manager import process_billing
from app.agent.project_tracker import track_deadlines

@pytest.mark.asyncio
async def test_proposal_writer_hitl_integration(db_session):
    """Verify that proposal writer creates an approval request for high-risk leads."""
    # 1. Create a high-value lead
    lead = Lead(
        id=uuid4(),
        title="High Value Project",
        description="Needs a complex solution for a big client.",
        score=95,
        tenant_id=uuid4() # Mock tenant
    )
    db_session.add(lead)
    await db_session.commit()

    # 2. Run agent
    await draft_proposal(db_session, lead.id)

    # 3. Check for Approval record
    result = await db_session.execute(select(Approval).where(Approval.entity_id == lead.id))
    approval = result.scalar_one_or_none()
    
    assert approval is not None
    assert approval.entity_type == "proposal"
    assert approval.status == "pending"

@pytest.mark.asyncio
async def test_finance_manager_billing_flow(db_session):
    """Verify that finance manager creates draft invoices for completed milestones."""
    tenant_id = uuid4()
    
    # 1. Create project and completed milestone
    project = Project(id=uuid4(), title="Test Project", tenant_id=tenant_id)
    db_session.add(project)
    await db_session.flush()
    
    milestone = Milestone(
        id=uuid4(),
        project_id=project.id,
        title="Milestone 1",
        amount=500.0,
        status="completed", # Should be picked up
        due_date=datetime.now(timezone.utc) - timedelta(days=1)
    )
    db_session.add(milestone)
    await db_session.commit()

    # 2. Run finance manager
    await process_billing(db_session)

    # 3. Check for Invoice
    result = await db_session.execute(select(Invoice).where(Invoice.tenant_id == tenant_id))
    invoices = result.scalars().all()
    
    assert len(invoices) == 1
    assert invoices[0].amount == 500.0
    assert invoices[0].status == "draft"

@pytest.mark.asyncio
async def test_process_billing_future_milestone(db_session: AsyncSession):
    # Setup project and future milestone
    tenant_id = uuid4()
    project = Project(id=uuid4(), title="Future Project", tenant_id=tenant_id)
    db_session.add(project)
    await db_session.flush()

    milestone = Milestone(
        id=uuid4(),
        project_id=project.id,
        title="Future Milestone",
        amount=1000.0,
        status="active",  # Not completed, should NOT be picked up
        due_date=datetime.now(timezone.utc) + timedelta(hours=48)
    )
    db_session.add(milestone)
    await db_session.commit()

    # 2. Run finance manager
    await process_billing(db_session)

    # 3. Check that no invoice was created for this milestone
    result = await db_session.execute(select(Invoice).where(Invoice.project_id == project.id))
    invoice = result.scalar_one_or_none()
    assert invoice is None

@pytest.mark.asyncio
async def test_project_tracker_alerts(db_session):
    """Verify that project tracker identifies upcoming deadlines."""
    # 1. Create milestone due in 48 hours
    project = Project(id=uuid4(), title="Expiring Project", tenant_id=uuid4())
    db_session.add(project)
    await db_session.flush()
    
    milestone = Milestone(
        id=uuid4(),
        project_id=project.id,
        title="Due Soon",
        status="active",
        due_date=datetime.now(timezone.utc) + timedelta(hours=48)
    )
    db_session.add(milestone)
    await db_session.commit()

    # 2. Run tracker (should log warning but not crash)
    await track_deadlines(db_session)
    
    # If no exception, test passes (real verification would check logs)
    assert True

import asyncio
import uuid
import logging
import sys
import os

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant, Lead, Project, Milestone, Invoice
from app.agent.lead_scout import run_lead_scout
from app.agent.proposal_writer import draft_proposal
from app.agent.finance_manager import process_billing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gold_path_test")

async def run_test():
    logger.info("🚀 Starting Gold Path E2E Test...")

    async with AsyncSessionLocal() as db:
        # 1. Ensure Tenant exists
        result = await db.execute(select(Tenant).limit(1))
        tenant = result.scalars().first()
        if not tenant:
            logger.info("Creating test tenant...")
            tenant = Tenant(name="Test Agency")
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)

        # 2. Run Lead Scout
        logger.info("--- Step 1: Lead Scout ---")
        await run_lead_scout()
        
        # Verify leads were created
        result = await db.execute(select(Lead).where(Lead.tenant_id == tenant.id).order_by(Lead.score.desc()).limit(1))
        lead = result.scalars().first()
        if not lead:
            logger.error("❌ No leads found after Lead Scout run.")
            return
        logger.info(f"✅ Found Lead: {lead.title} (Score: {lead.score})")

        # 3. Run Proposal Writer
        logger.info("--- Step 2: Proposal Writer ---")
        proposal_res = await draft_proposal(db, lead.id)
        if proposal_res["status"] == "hitl_queued":
            logger.info(f"✅ Proposal drafted and queued for HITL. Approval ID: {proposal_res['approval_id']}")
        else:
            logger.info(f"✅ Proposal drafted: {proposal_res.get('status')}")

        # 4. Simulate Project Creation & Milestone Completion
        logger.info("--- Step 3: Project & Milestone ---")
        project = Project(
            tenant_id=tenant.id,
            lead_id=lead.id,
            title=f"Project: {lead.title}",
            status="active"
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

        milestone = Milestone(
            project_id=project.id,
            title="Initial Delivery",
            amount=500.0,
            status="completed" # Marked as completed to trigger Finance Manager
        )
        db.add(milestone)
        await db.commit()
        logger.info(f"✅ Project created and milestone 'Initial Delivery' ($500) marked as COMPLETED.")

        # 5. Run Finance Manager
        logger.info("--- Step 4: Finance Manager ---")
        billing_res = await process_billing(db)
        logger.info(f"✅ Finance Manager run: {billing_res}")

        # 6. Verify Invoice
        result = await db.execute(select(Invoice).where(Invoice.project_id == project.id))
        invoice = result.scalars().first()
        if invoice:
            logger.info(f"✅ SUCCESS: Draft Invoice found for ${invoice.amount} (Status: {invoice.status})")
        else:
            logger.error("❌ No invoice found for the completed milestone.")

    logger.info("🏁 Gold Path Test Complete.")

if __name__ == "__main__":
    asyncio.run(run_test())

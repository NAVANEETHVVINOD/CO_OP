import logging
import uuid
from typing import Dict, Any, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Invoice, Project, Milestone, Tenant
from app.communication.telegram import send_message

logger = logging.getLogger(__name__)

async def process_billing(db: AsyncSession):
    """
    Agent: Finance Manager.
    Scans for completed milestones and generates draft invoices.
    """
    logger.info("Finance Manager: Scanning for billable milestones...")
    
    # 1. Get all completed milestones
    result = await db.execute(
        select(Milestone, Project)
        .join(Project, Milestone.project_id == Project.id)
        .where(Milestone.status == "completed")
    )
    completed_milestones = result.all()
    
    invoices_created = 0
    for milestone, project in completed_milestones:
        # 2. Check if an invoice already exists for this milestone's amount and project
        # (Simple heuristic for Stage 3)
        invoice_result = await db.execute(
            select(Invoice).where(
                and_(
                    Invoice.project_id == project.id,
                    Invoice.amount == milestone.amount,
                    Invoice.status == "draft"
                )
            )
        )
        existing_invoice = invoice_result.scalar_one_or_none()
        
        if not existing_invoice and milestone.amount > 0:
            # 3. Create Draft Invoice
            new_invoice = Invoice(
                tenant_id=project.tenant_id,
                project_id=project.id,
                amount=milestone.amount,
                status="draft",
                currency="USD"
            )
            db.add(new_invoice)
            invoices_created += 1
            
            # 4. Notify via Telegram
            msg = (
                f"💰 *New Draft Invoice*\n"
                f"Project: {project.title}\n"
                f"Milestone: {milestone.title}\n"
                f"Amount: ${milestone.amount:.2f}\n"
                f"Status: Scanned and Drafted ✅"
            )
            try:
                await send_message(msg)
            except Exception as e:
                logger.warning(f"Failed to send Telegram notification: {e}")

    if invoices_created > 0:
        await db.commit()
        logger.info(f"Finance Manager: Created {invoices_created} new draft invoices.")
    else:
        logger.info("Finance Manager: No new billable milestones found.")
    
    return {"status": "complete", "invoices_created": invoices_created}

async def create_invoice(db: AsyncSession, project_id: uuid.UUID, amount: float) -> Invoice:
    """Creates a new draft invoice manually."""
    project_res = await db.execute(select(Project).where(Project.id == project_id))
    project = project_res.scalar_one_or_none()
    
    if not project:
        raise ValueError("Project not found")

    invoice = Invoice(
        tenant_id=project.tenant_id,
        project_id=project_id,
        amount=amount,
        status="draft"
    )
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice

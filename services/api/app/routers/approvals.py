from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Approval, User
from app.dependencies import verify_token
from app.schemas.approval import Approval as ApprovalSchema
import uuid

router = APIRouter(prefix="/v1/approvals", tags=["Approvals"])

@router.get("", response_model=List[ApprovalSchema])
async def list_approvals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    """
    Returns the HITL approval queue for the current tenant's Stage 3 agents.
    Includes proposals, invoices, and outreach actions.
    """
    result = await db.execute(
        select(Approval)
        .where(Approval.tenant_id == current_user.tenant_id)
        .order_by(Approval.created_at.desc())
    )
    return result.scalars().all()

import uuid

@router.post("/{approval_id}/approve")
async def approve_action(
    approval_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    """Approve a queued action and trigger its execution."""
    result = await db.execute(
        select(Approval)
        .where(Approval.id == approval_id)
        .where(Approval.tenant_id == current_user.tenant_id)
    )
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval.status = "approved"
    
    # Stage 3 Logic: Trigger OutreachManager if entity_type is 'proposal'
    if approval.entity_type == "proposal":
        from app.agent.outreach_manager import submit_outreach
        await submit_outreach(approval.entity_id, approval.data)

    await db.commit()
    return {"status": "success", "message": f"Action {approval_id} approved."}

@router.post("/{approval_id}/reject")
async def reject_action(
    approval_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    """Reject a queued action."""
    result = await db.execute(
        select(Approval)
        .where(Approval.id == approval_id)
        .where(Approval.tenant_id == current_user.tenant_id)
    )
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval.status = "rejected"
    await db.commit()
    return {"status": "success", "message": f"Action {approval_id} rejected."}

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Project, Milestone, User
from app.dependencies import verify_token
from sqlalchemy.orm import selectinload
from app.schemas.project import ProjectResponse, MilestoneResponse

router = APIRouter(prefix="/v1/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    """Returns all active projects for the current tenant."""
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.milestones))
        .where(Project.tenant_id == current_user.tenant_id)
        .order_by(Project.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{project_id}/milestones", response_model=List[MilestoneResponse])
async def get_milestones(
    project_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    """Returns milestones for a specific project within the tenant."""
    result = await db.execute(
        select(Milestone)
        .join(Project)
        .where(Project.id == project_id)
        .where(Project.tenant_id == current_user.tenant_id)
    )
    return result.scalars().all()
import uuid

@router.post("/milestones/{milestone_id}/complete")
async def complete_milestone(
    milestone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    """Marks a milestone as completed."""
    result = await db.execute(
        select(Milestone)
        .join(Project)
        .where(Milestone.id == milestone_id)
        .where(Project.tenant_id == current_user.tenant_id)
    )
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    milestone.status = "completed"
    await db.commit()
    
    return {"status": "success", "message": f"Milestone {milestone_id} completed."}

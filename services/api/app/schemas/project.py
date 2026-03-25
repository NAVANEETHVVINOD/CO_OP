from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
import uuid

class MilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "pending"

class Milestone(MilestoneBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MilestoneResponse(MilestoneBase):
    id: uuid.UUID
    created_at: datetime
    # Add other fields if needed
    model_config = ConfigDict(from_attributes=True)

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = ""
    status: str = "active"

class ProjectCreate(ProjectBase):
    lead_id: Optional[uuid.UUID] = None

class Project(ProjectBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    lead_id: Optional[uuid.UUID] = None
    created_at: datetime
    milestones: List[Milestone] = []
    model_config = ConfigDict(from_attributes=True)

class ProjectResponse(ProjectBase):
    id: uuid.UUID
    created_at: datetime
    milestones: List[MilestoneResponse] = []
    model_config = ConfigDict(from_attributes=True)

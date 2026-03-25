from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict
import uuid

class ApprovalBase(BaseModel):
    risk_level: str = "LOW"
    entity_type: str
    entity_id: uuid.UUID
    data: Dict[str, Any] = {}
    status: str = "pending"

class Approval(ApprovalBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    action_type: str
    description: str
    proposed_by: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

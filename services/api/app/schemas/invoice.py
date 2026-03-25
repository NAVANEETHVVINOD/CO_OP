from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
import uuid

class InvoiceBase(BaseModel):
    project_id: uuid.UUID
    amount: float
    currency: str = "USD"
    status: str = "draft"
    due_date: Optional[datetime] = None

class Invoice(InvoiceBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InvoiceResponse(InvoiceBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

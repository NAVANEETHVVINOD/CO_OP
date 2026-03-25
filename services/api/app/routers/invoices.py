from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Invoice, User
from app.dependencies import verify_token
from app.schemas.invoice import InvoiceResponse

router = APIRouter(prefix="/v1/invoices", tags=["Finance"])

@router.get("", response_model=List[InvoiceResponse])
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_token)
):
    """Returns all project invoices for the current tenant."""
    result = await db.execute(
        select(Invoice)
        .where(Invoice.tenant_id == current_user.tenant_id)
        .order_by(Invoice.created_at.desc())
    )
    return result.scalars().all()

from fastapi import APIRouter

router = APIRouter(prefix="/v1/approvals", tags=["approvals"])

@router.get("")
async def list_approvals():
    # Stage 1 stub — returns empty array.
    # Frontend (AppSidebar, ApprovalsPage) expects a plain array.
    # Full HITL approval system is built in Stage 3 (T-051).
    return []

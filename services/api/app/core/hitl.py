import uuid
from enum import Enum
from typing import Any, Dict, Optional
from app.db.models import Approval, Tenant
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class RiskLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class HITLManager:
    @staticmethod
    def classify_risk(entity_type: str, action: str, data: Dict[str, Any]) -> RiskLevel:
        """
        Classifies the risk of an agent action based on type and payload.
        """
        if entity_type == "outreach":
            # Direct client contact is always at least HIGH risk in Stage 3
            return RiskLevel.HIGH
        
        if entity_type == "invoice":
            amount = data.get("amount", 0)
            if amount > 5000:
                return RiskLevel.CRITICAL
            if amount > 1000:
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM
            
        if entity_type == "proposal":
            score = data.get("score", 0)
            if score > 90:
                return RiskLevel.MEDIUM # High confidence, still want a peek
            return RiskLevel.HIGH
            
        return RiskLevel.LOW

    @staticmethod
    def needs_approval(risk_level: RiskLevel) -> bool:
        """Determines if an action requires explicit human approval."""
        return risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]

    @staticmethod
    async def create_approval_request(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        risk_level: RiskLevel,
        data: Dict[str, Any]
    ) -> Approval:
        """Records a new approval request in the HITL queue."""
        approval = Approval(
            tenant_id=tenant_id,
            risk_level=risk_level.value,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            status="pending"
        )
        db.add(approval)
        await db.commit()
        await db.refresh(approval)
        return approval

hitl_manager = HITLManager()

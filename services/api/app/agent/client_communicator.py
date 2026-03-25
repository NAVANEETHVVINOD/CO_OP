import logging
import uuid
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ClientMemory
from app.core.simulation import is_simulation_mode

logger = logging.getLogger(__name__)

async def handle_client_interaction(db: AsyncSession, tenant_id: uuid.UUID, client_id: str, message: str) -> Dict[str, Any]:
    """
    Agent: Client Communicator.
    Manages client memory, updates JSONB relationship data, and triggers alerts
    if a message contains high-risk triggers (payment/budget disputes).
    """
    # 1. Update/Create Client Memory
    result = await db.execute(select(ClientMemory).where(ClientMemory.client_id == client_id))
    mem_record = result.scalar_one_or_none()
    
    if not mem_record:
        mem_record = ClientMemory(
            tenant_id=tenant_id,
            client_id=client_id,
            memory={"history": [message], "sentiment": "neutral"}
        )
        db.add(mem_record)
    else:
        # Update JSONB history (PostgreSQL specific optimization)
        history = mem_record.memory.get("history", [])
        history.append(message)
        mem_record.memory["history"] = history[-20:] # Keep last 20
        mem_record.memory["last_interaction"] = message

    # 2. Extract Intent/Risk
    risk_found = any(word in message.lower() for word in ["budget", "price", "expensive", "stop", "cancel"])
    
    await db.commit()
    
    if risk_found:
        logger.warning(f"High-risk intent detected from client {client_id}: {message}")
        return {"status": "escalated", "reason": "High-risk keywords found"}

    return {"status": "acknowledged", "memory_id": mem_record.id}

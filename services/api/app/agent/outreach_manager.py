import logging
import uuid
from typing import Dict, Any
from app.core.simulation import is_simulation_mode, simulation_engine

logger = logging.getLogger(__name__)

async def submit_outreach(lead_id: uuid.UUID, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent: Outreach Manager.
    Executes the actual submission of a proposal to an external platform. 
    Can be called manually after HITL approval or automatically for low-risk actions.
    """
    logger.info(f"Executing outreach for lead {lead_id}")
    
    if is_simulation_mode():
        return await simulation_engine.mock_external_call(
            service="upwork",
            action="submit_proposal",
            payload=payload
        )

    # In Stage 3, we mock real calls here to avoid leaking real proposals.
    # In Stage 4, this would use Composio or a dedicated platform bridge.
    logger.info(f"[PROD-STUB] Submitting real outreach for {lead_id}")
    return {
        "status": "success",
        "real_submission": False,
        "message": "Outreach submitted (simulated for safety)."
    }

import os
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def is_simulation_mode() -> bool:
    """
    Returns True if the system is running in simulation mode.
    In simulation mode, no real external API calls (Upwork, etc.) are made.
    """
    return os.getenv("COOP_SIMULATION_MODE", "false").lower() == "true"

class SimulationEngine:
    @staticmethod
    async def mock_external_call(service: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates an external API call and returns a successful mock response.
        """
        logger.info(f"[SIMULATION] Mocking {service} {action} with payload keys: {list(payload.keys())}")
        
        if service == "upwork":
            return {
                "status": "success",
                "external_id": f"sim_upwork_{os.urandom(4).hex()}",
                "message": "Simulated successful submission to Upwork."
            }
        
        if service == "email":
            return {
                "status": "sent",
                "recipient": payload.get("to"),
                "subject": payload.get("subject")
            }
            
        return {"status": "success", "mock": True}

simulation_engine = SimulationEngine()

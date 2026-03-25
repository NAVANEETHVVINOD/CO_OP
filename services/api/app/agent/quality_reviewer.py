import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

async def check_quality(content: str, job_description: str) -> Dict[str, Any]:
    """
    Agent: Quality Reviewer.
    Provides a base verification of documents, proposals, or code snippets
    before they are marked as ready for HITL approval.
    """
    # 1. Base checks (spelling, basic coherence)
    # In Phase 4, this triggers a LiteLLM "Reviewer" prompt.
    
    score = 1.0 # default
    issues: List[str] = []
    
    if len(content) < 50:
        score -= 0.5
        issues.append("Content significantly shorter than expected.")
    
    if any(word in content.lower() for word in ["as an ai", "i cannot", "placeholder"]):
        score -= 0.8
        issues.append("Found AI-refusal or placeholder text.")

    logger.info(f"[QUALITY] Review completed. Score: {score}. Issues: {len(issues)}")
    
    return {
        "status": "passed" if score > 0.6 else "failed",
        "score": score,
        "issues": issues
    }

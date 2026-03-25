import logging
import uuid
import httpx
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Lead
from app.core.hitl import hitl_manager
from app.core.simulation import is_simulation_mode
from app.config import get_settings
from app.services.vector_search import search_relevant_chunks

logger = logging.getLogger(__name__)
settings = get_settings()

async def draft_proposal(db: AsyncSession, lead_id: uuid.UUID) -> Dict[str, Any]:
    """
    Agent: Proposal Writer.
    Gathers lead details, retrieves relevant portfolio items via RAG, 
    drafts a matching pitch using LiteLLM, and determines if HITL approval is required.
    """
    # 1. Fetch Lead details
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        logger.error(f"Lead {lead_id} not found")
        return {"status": "error", "message": "Lead not found"}

    # 2. Portfolio RAG (Real retrieval from Qdrant)
    try:
        relevant_chunks = await search_relevant_chunks(str(lead.tenant_id), f"{lead.title} {lead.description[:500]}", limit=4)
        portfolio_context = "\n".join([f"- {c['text']}" for c in relevant_chunks])
    except Exception as e:
        logger.warning(f"RAG retrieval failed for proposal drafting: {e}")
        portfolio_context = "Expertise in Python, FastAPI, AI Agents, and RAG Pipelines."

    # 3. LLM synthesis
    system_prompt = (
        "You are 'Co-Op', a premium AI-driven software agency. Your goal is to draft a compelling, "
        "evidence-based Upwork proposal that directly addresses the client's needs using your past experience."
    )

    user_msg = f"""
Draft a professional, concise Upwork proposal for the following job:
Title: {lead.title}
Description: {lead.description}

### Relevant Experience from our Portfolio:
{portfolio_context}

### Guidelines:
1. Be direct and avoid generic fluff.
2. Mention 1-2 specific projects or skills from our portfolio that match their needs.
3. Propose a clear first step (e.g., 'I can show you a demo of our similar RAG pipeline').
4. Keep it under 250 words.
"""
    
    proposal_text = "[MOCK PROPOSAL] I see you need a RAG pipeline. We've built several similar systems using FastAPI and Qdrant. I'd love to discuss how we can help."
    
    # 4. Real LiteLLM call
    if settings.LITELLM_URL and not is_simulation_mode():
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{settings.LITELLM_URL}/v1/chat/completions",
                    json={
                        "model": "simple",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_msg}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.3
                    },
                    timeout=45.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    proposal_text = data["choices"][0]["message"]["content"].strip()
                else:
                    logger.warning(f"LiteLLM call failed with status {resp.status_code}, using mock.")
        except Exception as e:
            logger.warning(f"LiteLLM call failed exception, using mock: {e}")

    # 5. Risk Classification & HITL
    # Outreach always starts at MEDIUM risk for A3
    risk = hitl_manager.classify_risk("proposal", "submit", {"score": lead.score})
    
    # Force HITL for v1.0 unless explicitly automated
    if hitl_manager.needs_approval(risk) or True:
        approval = await hitl_manager.create_approval_request(
            db=db,
            tenant_id=lead.tenant_id,
            entity_type="proposal",
            entity_id=lead_id,
            risk_level=risk,
            data={
                "proposal_text": proposal_text, 
                "lead_title": lead.title,
                "lead_url": lead.url,
                "rag_snippets": [c['text'] for c in relevant_chunks] if 'relevant_chunks' in locals() else []
            }
        )
        logger.info(f"Proposal for lead {lead_id} queued for HITL (Risk: {risk.value})")
        return {"status": "hitl_queued", "approval_id": approval.id}

    # 6. Direct Ready (Rare for outreach in Stage 3)
    return {"status": "ready", "proposal_text": proposal_text}

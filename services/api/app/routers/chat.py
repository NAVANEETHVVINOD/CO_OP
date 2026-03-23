import json
import logging
import asyncio
import uuid
from typing import List, Dict, Any, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.dependencies import verify_token
from app.db.models import User
from app.agent.graph import research_agent

router = APIRouter(prefix="/v1/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    conversation_id: str | None = None

async def generate_chat_stream(request: ChatRequest, tenant_id: str, user_id: str) -> AsyncGenerator[dict[str, str], None]:
    try:
        # Run the FULL LangGraph pipeline: retrieve_docs → rerank_results → generate_answer
        result = await research_agent.ainvoke({
            "tenant_id": tenant_id,
            "question": request.message,
            "chat_history": request.history,
            "retrieved_docs": [],
            "reranked_docs": [],
            "final_answer": ""
        })
        
        # Extract results
        reranked_docs = result.get("reranked_docs", [])
        final_answer = result.get("final_answer", "No answer generated.")
        
        # Yield citations from reranked docs
        for idx, doc in enumerate(reranked_docs[:5]):
            citation_data = {
                "source": str(doc.get("document_id", "unknown")),
                "chunk_index": doc.get("chunk_index", idx),
                "page": idx + 1,
                "score": round(doc.get("rerank_score", doc.get("rrf_score", 0.0)), 3)
            }
            yield {"event": "citation", "data": json.dumps(citation_data)}
        
        # Stream the final answer word-by-word
        words = final_answer.split(" ")
        for word in words:
            yield {"event": "token", "data": json.dumps({"content": word + " "})}
            await asyncio.sleep(0.03)
        
        # Send done event
        yield {"event": "done", "data": json.dumps({
            "conversation_id": request.conversation_id or str(uuid.uuid4()),
            "total_chunks": len(reranked_docs),
            "cost_usd": 0.0
        })}
        
    except Exception as e:
        logger.error(f"Error in chat stream: {e}", exc_info=True)
        yield {"event": "token", "data": json.dumps({"content": f"\n\nError: {str(e)}"})}
        yield {"event": "done", "data": json.dumps({"conversation_id": "error", "cost_usd": 0.0})}

@router.post("/stream")
async def chat_stream(
    request: Request,
    chat_req: ChatRequest,
    current_user: User = Depends(verify_token)
):
    if not chat_req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    return EventSourceResponse(
        generate_chat_stream(chat_req, str(current_user.tenant_id), str(current_user.id)),
        headers={
            "Cache-Control": "no-cache",
            "Content-Type": "text/event-stream"
        }
    )


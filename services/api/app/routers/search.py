from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import verify_token
from app.db.models import User
from app.services.search import hybrid_search

router = APIRouter(prefix="/v1/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    document_id: str
    chunk_index: int
    text: str
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

@router.post("", response_model=SearchResponse)
async def perform_search(
    request: SearchRequest,
    current_user: User = Depends(verify_token)
):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    raw_results = await hybrid_search(
        query=request.query,
        tenant_id=current_user.tenant_id,
        top_k=request.top_k
    )
    
    formatted_results = []
    for hit in raw_results:
        formatted_results.append(SearchResult(
            document_id=hit.get("document_id", ""),
            chunk_index=hit.get("chunk_index", 0),
            text=hit.get("text", ""),
            score=hit.get("rerank_score", hit.get("rrf_score", 0.0))
        ))
        
    return SearchResponse(results=formatted_results)

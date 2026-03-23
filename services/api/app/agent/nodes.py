import os
import uuid
from typing import Dict, Any, List

from app.agent.state import AgentState
from app.services.search import _perform_search, _compute_rrf, embedder, bm25_encoder, qdrant, models
from app.services.reranker import reranker

async def retrieve_docs(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    tenant_id = state["tenant_id"]
    
    # 1. Embed query (dense and sparse)
    dense_vector = await embedder.embed_text(question)
    sparse_indices, sparse_values = bm25_encoder.encode(question)
    sparse_vector = models.SparseVector(indices=sparse_indices, values=sparse_values)
    
    # 2. Execute parallel searches
    import asyncio
    dense_task = _perform_search(dense_vector, "dense", tenant_id, limit=50)
    sparse_task = _perform_search(sparse_vector, "sparse", tenant_id, limit=50)
    
    dense_results, sparse_results = await asyncio.gather(dense_task, sparse_task)
    
    # 3. Apply Reciprocal Rank Fusion
    rrf_candidates = _compute_rrf(dense_results, sparse_results, alpha=0.7, k=60)[:20]
    
    return {"retrieved_docs": rrf_candidates}

async def rerank_results(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    docs = state.get("retrieved_docs", [])
    
    if not docs:
        return {"reranked_docs": []}
        
    final_results = await reranker.rerank(query=question, documents=docs, top_k=10)
    
    return {"reranked_docs": final_results}

async def generate_answer(state: AgentState) -> Dict[str, Any]:
    """
    Stub inference: generates a context-based markdown response with inline citations.
    No external LLM required. This synthesizes retrieved context into a readable answer.
    """
    question = state["question"]
    docs = state.get("reranked_docs", [])
    
    if not docs:
        return {"final_answer": "I could not find any relevant documents to answer your question. Please upload more documents or try a different query."}
    
    # Build a markdown response from the retrieved chunks
    lines: List[str] = []
    lines.append(f"## Answer to: *{question}*\n")
    lines.append("Based on the retrieved documents, here is what I found:\n")
    
    for i, doc in enumerate(docs[:5]):
        text = doc.get("text", "").strip()
        doc_id = doc.get("document_id", "unknown")[:8]
        chunk_idx = doc.get("chunk_index", i)
        score = doc.get("rerank_score", doc.get("rrf_score", 0.0))
        
        # Take first 300 chars of each chunk as a summary
        summary = text[:300] + "..." if len(text) > 300 else text
        lines.append(f"**[{i+1}]** *(Doc {doc_id}, Chunk {chunk_idx}, Score: {score:.3f})*")
        lines.append(f"> {summary}\n")
    
    lines.append("\n---")
    lines.append(f"*Found {len(docs)} relevant chunks across your document library.*")
    
    final_answer = "\n".join(lines)
    return {"final_answer": final_answer}

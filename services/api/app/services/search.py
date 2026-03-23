import asyncio
import uuid
from typing import Any

from qdrant_client import models
from qdrant_client.models import ScoredPoint

from app.db.qdrant_client import qdrant, COLLECTION_NAME
from app.core.embedder import embedder
from app.services.bm25_encoder import bm25_encoder
from app.services.reranker import reranker


async def _perform_search(
    query_vector: Any, vector_name: str, tenant_id: str, limit: int = 100
) -> list[ScoredPoint]:
    result = await qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        using=vector_name,
        query_filter=models.Filter(
            must=[models.FieldCondition(key="tenant_id", match=models.MatchValue(value=tenant_id))]
        ),
        limit=limit,
        with_payload=True
    )
    return result.points


def _compute_rrf(
    dense_results: list[ScoredPoint],
    sparse_results: list[ScoredPoint],
    alpha: float = 0.7,
    k: int = 60,
) -> list[dict[str, Any]]:
    scores: dict[Any, float] = {}
    items: dict[Any, dict[str, Any]] = {}

    # Process dense results
    for rank, hit in enumerate(dense_results):
        item_id = hit.id
        items[item_id] = hit.payload or {}
        if item_id not in scores:
            scores[item_id] = 0.0
        scores[item_id] += alpha * (1.0 / (k + rank + 1))

    # Process sparse results
    for rank, hit in enumerate(sparse_results):
        item_id = hit.id
        if item_id not in items:
            items[item_id] = hit.payload or {}
        if item_id not in scores:
            scores[item_id] = 0.0
        scores[item_id] += (1.0 - alpha) * (1.0 / (k + rank + 1))

    # Sort by accumulated RRF score
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    results: list[dict[str, Any]] = []
    for item_id, score in sorted_items:
        payload = items[item_id].copy()
        payload["rrf_score"] = score
        results.append(payload)

    return results


async def hybrid_search(query: str, tenant_id: uuid.UUID, top_k: int = 5) -> list[dict[str, Any]]:
    """
    Combines dense and sparse search using Reciprocal Rank Fusion (RRF, alpha=0.7)
    and then reranks the top 20 candidate chunks using ms-marco-MiniLM-L-6-v2.
    """
    tenant_str = str(tenant_id)

    # 1. Embed query (dense and sparse)
    dense_vector = await embedder.embed_text(query)
    sparse_indices, sparse_values = bm25_encoder.encode(query)
    sparse_vector = models.SparseVector(indices=sparse_indices, values=sparse_values)

    # 2. Execute parallel searches
    dense_task = _perform_search(dense_vector, "dense", tenant_str, limit=50)
    sparse_task = _perform_search(sparse_vector, "sparse", tenant_str, limit=50)

    dense_results, sparse_results = await asyncio.gather(dense_task, sparse_task)

    # 3. Apply Reciprocal Rank Fusion (alpha=0.7 implies weighted RRF)
    # We take the top 20 candidate chunks from RRF for reranking
    rrf_candidates = _compute_rrf(dense_results, sparse_results, alpha=0.7, k=60)[:20]

    # 4. Rerank using CrossEncoder
    final_results = await reranker.rerank(query=query, documents=rrf_candidates, top_k=top_k)

    return final_results

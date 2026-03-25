import logging
from typing import List, Dict, Any
from app.db.qdrant_client import qdrant, COLLECTION_NAME
from app.core.embedder import embedder
from qdrant_client import models

logger = logging.getLogger(__name__)

async def search_relevant_chunks(tenant_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for relevant document chunks in Qdrant using hybrid search (dense + sparse).
    """
    if not qdrant:
        logger.warning("Qdrant is not initialized. Returning empty results.")
        return []

    try:
        # 1. Generate dense embedding
        dense_vector = await embedder.embed_text(query)

        results = await qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="tenant_id",
                        match=models.MatchValue(value=tenant_id),
                    )
                ]
            ),
            query=dense_vector,
            using="dense",
            limit=limit,
            with_payload=True,
        )

        return [
            {
                "text": hit.payload.get("text", ""),
                "score": hit.score,
                "document_id": hit.payload.get("document_id"),
            }
            for hit in results.points
        ]

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []

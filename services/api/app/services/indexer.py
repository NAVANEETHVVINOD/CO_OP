import uuid
from typing import List, Dict, Any
from qdrant_client.models import PointStruct
from app.db.qdrant_client import qdrant, COLLECTION_NAME
from app.core.embedder import embedder
from app.services.bm25_encoder import bm25_encoder

async def upsert_document_chunks_to_qdrant(tenant_id: uuid.UUID, document_uuid: uuid.UUID, chunks_text: List[str]):
    """
    Batch upserts document chunks to Qdrant, generating both dense and sparse vectors natively.
    """
    if not chunks_text:
        return

    # Generate dense embeddings (batch)
    dense_embeddings = await embedder.embed_batch(chunks_text)
    
    # Generate sparse embeddings (sequential/fast enough locally)
    sparse_embeddings = [bm25_encoder.encode(text) for text in chunks_text]

    points = []
    
    for idx, (text, dense_emb, (sparse_indices, sparse_values)) in enumerate(zip(chunks_text, dense_embeddings, sparse_embeddings)):
        chunk_id = str(uuid.uuid4())
        
        point = PointStruct(
            id=chunk_id,
            vector={
                "dense": dense_emb,
                "sparse": {
                    "indices": sparse_indices,
                    "values": sparse_values
                }
            },
            payload={
                "tenant_id": str(tenant_id),
                "document_id": str(document_uuid),
                "chunk_index": idx,
                "text": text,
            }
        )
        points.append(point)

    # Upsert all points
    await qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )

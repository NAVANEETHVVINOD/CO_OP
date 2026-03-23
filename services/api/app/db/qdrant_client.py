from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, SparseVectorParams
from app.config import get_settings

settings = get_settings()

# Initialize async Qdrant client
qdrant = AsyncQdrantClient(url=settings.QDRANT_URL, check_compatibility=False)

COLLECTION_NAME = "co_op_documents"

async def init_qdrant() -> None:
    # Check if the collection exists
    exists = await qdrant.collection_exists(collection_name=COLLECTION_NAME)
    
    if not exists:
        # Create a hybrid collection (dense + sparse)
        from qdrant_client import models
        await qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "dense": VectorParams(
                    size=384, # Size for all-MiniLM-L6-v2
                    distance=Distance.COSINE
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    modifier=models.Modifier.IDF
                )
            }
        )

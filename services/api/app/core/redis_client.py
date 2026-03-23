import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True
)

DOCUMENT_INGESTION_QUEUE = "document_ingestion_queue"

async def publish_ingestion_event(document_id: str, file_path: str, tenant_id: str, filename: str):
    await redis_client.xadd(
        DOCUMENT_INGESTION_QUEUE,
        {
            "document_id": document_id,
            "file_path": file_path,
            "tenant_id": tenant_id,
            "filename": filename
        }
    )

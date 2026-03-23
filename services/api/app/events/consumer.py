import asyncio
import logging
from uuid import UUID

from app.core.redis_client import redis_client, DOCUMENT_INGESTION_QUEUE
from app.db.session import AsyncSessionLocal
from app.db.repositories import DocumentRepository
from app.services.parser import parser
from app.services.chunker import SemanticChunker
from app.services.indexer import upsert_document_chunks_to_qdrant
from app.core.minio_client import get_file, upload_file
import json

logger = logging.getLogger(__name__)

# Basic consumer group setup
CONSUMER_GROUP = "doc_ingestion_group"
CONSUMER_NAME = "worker_1"

async def setup_redis_stream():
    try:
        await redis_client.xgroup_create(DOCUMENT_INGESTION_QUEUE, CONSUMER_GROUP, mkstream=True)
    except Exception as e:
        if "BUSYGROUP" not in str(e):
            logger.error(f"Error creating consumer group: {e}")

async def process_document(document_id: str, file_path: str, tenant_id: str, filename: str):
    async with AsyncSessionLocal() as db:
        repo = DocumentRepository(db)
        doc = await repo.get(UUID(document_id))
        if not doc:
            logger.error(f"Document {document_id} not found in DB")
            return

        try:
            # 1. Parse document into text
            file_bytes = get_file("raw-documents", file_path)
            if not file_bytes:
                logger.error(f"File {file_path} not found in MinIO")
                raise Exception("File not found in MinIO")

            text = parser.parse(filename, file_bytes)

            # 2. Chunk text
            chunker = SemanticChunker(chunk_size=512, overlap=64)
            chunks = chunker.chunk_text(text)

            # 2.5 Store parsed chunks in MinIO
            chunks_json = json.dumps([{"chunk_index": i, "text": chunk} for i, chunk in enumerate(chunks)]).encode("utf-8")
            parsed_object_name = file_path.rsplit(".", 1)[0] + ".json"
            upload_success = upload_file("parsed-chunks", parsed_object_name, chunks_json, content_type="application/json")
            if not upload_success:
                logger.warning(f"Failed to upload parsed chunks to MinIO for {file_path}")

            # 3. Index in Qdrant hybrid collection
            await upsert_document_chunks_to_qdrant(
                tenant_id=UUID(tenant_id),
                document_uuid=UUID(document_id),
                chunks_text=chunks
            )

            # 4. Update status to READY
            doc.status = "READY"
            await db.commit()
            logger.info(f"Successfully processed document {document_id}")

        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            doc.status = "FAILED"
            await db.commit()

async def consume_ingestion_events():
    await setup_redis_stream()
    logger.info("Started Redis Document Ingestion Consumer")

    while True:
        try:
            # Read from stream: count=10, block=5000ms
            result = await redis_client.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {DOCUMENT_INGESTION_QUEUE: ">"},
                count=10,
                block=5000
            )

            if result:
                for stream, messages in result:
                    for message_id, message_data in messages:
                        doc_id = message_data.get("document_id")
                        file_path = message_data.get("file_path")
                        tenant_id = message_data.get("tenant_id")
                        filename = message_data.get("filename")
                        retries = int(message_data.get("retries", 0))

                        if doc_id and file_path and tenant_id and filename:
                            try:
                                await process_document(doc_id, file_path, tenant_id, filename)
                                # Acknowledge on success
                                await redis_client.xack(DOCUMENT_INGESTION_QUEUE, CONSUMER_GROUP, message_id)
                            except Exception as e:
                                logger.error(f"Error processing document {doc_id}: {e}")
                                retries += 1
                                if retries >= 3:
                                    logger.error(f"Document {doc_id} failed 3 times. Sending to DLQ.")
                                    # Write to DLQ
                                    await redis_client.xadd(f"{DOCUMENT_INGESTION_QUEUE}_dlq", message_data)
                                    # Acknowledge to remove from main queue
                                    await redis_client.xack(DOCUMENT_INGESTION_QUEUE, CONSUMER_GROUP, message_id)
                                else:
                                    # Not acknowledging will leave it in pending state. 
                                    # For a simple retry we can update the message or rely on pending message claiming.
                                    pass

        except Exception as e:
            logger.error(f"Error reading from stream: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(consume_ingestion_events())

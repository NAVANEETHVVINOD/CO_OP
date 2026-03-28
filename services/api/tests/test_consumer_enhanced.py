"""Enhanced tests for Redis events consumer."""
import pytest
import uuid
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.events.consumer import (
    setup_redis_stream,
    process_document
)


@pytest.mark.asyncio
async def test_setup_redis_stream_creates_group():
    """Test that setup creates consumer group"""
    with patch("app.events.consumer.redis_client") as mock_redis:
        mock_redis.xgroup_create = AsyncMock()
        
        await setup_redis_stream()
        
        mock_redis.xgroup_create.assert_called_once()
        call_args = mock_redis.xgroup_create.call_args
        assert "doc_ingestion_group" in call_args[0]


@pytest.mark.asyncio
async def test_setup_redis_stream_handles_existing_group():
    """Test that setup handles existing consumer group"""
    with patch("app.events.consumer.redis_client") as mock_redis:
        mock_redis.xgroup_create.side_effect = Exception("BUSYGROUP Consumer Group name already exists")
        
        # Should not raise exception
        await setup_redis_stream()


@pytest.mark.asyncio
async def test_setup_redis_stream_handles_other_errors():
    """Test that setup handles other Redis errors"""
    with patch("app.events.consumer.redis_client") as mock_redis:
        mock_redis.xgroup_create.side_effect = Exception("Connection error")
        
        # Should not raise exception
        await setup_redis_stream()


@pytest.mark.asyncio
async def test_process_document_success(db_session):
    """Test successful document processing"""
    from app.db.models import Document, Tenant
    
    # Create test tenant and document
    tenant = Tenant(name="test_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        title="test.txt",
        content_hash="hash123",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        with patch("app.events.consumer.parser") as mock_parser:
            with patch("app.events.consumer.SemanticChunker") as mock_chunker_class:
                with patch("app.events.consumer.upsert_document_chunks_to_qdrant") as mock_upsert:
                    with patch("app.events.consumer.upload_file") as mock_upload:
                        # Mock file retrieval
                        mock_get_file.return_value = b"Test document content"
                        
                        # Mock parser
                        mock_parser.parse.return_value = "Parsed text content"
                        
                        # Mock chunker
                        mock_chunker = MagicMock()
                        mock_chunker.chunk_text.return_value = ["Chunk 1", "Chunk 2"]
                        mock_chunker_class.return_value = mock_chunker
                        
                        # Mock upload
                        mock_upload.return_value = True
                        
                        # Mock Qdrant upsert
                        mock_upsert.return_value = None
                        
                        await process_document(
                            str(doc.id),
                            "test.txt",
                            str(tenant.id),
                            "test.txt"
                        )
    
    # Verify document status updated
    await db_session.refresh(doc)
    assert doc.status == "READY"


@pytest.mark.asyncio
async def test_process_document_file_not_found(db_session):
    """Test document processing when file not found in MinIO"""
    from app.db.models import Document, Tenant
    
    tenant = Tenant(name="test_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        title="missing.txt",
        content_hash="hash123",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        mock_get_file.return_value = None
        
        await process_document(
            str(doc.id),
            "missing.txt",
            str(tenant.id),
            "missing.txt"
        )
    
    # Verify document status updated to FAILED
    await db_session.refresh(doc)
    assert doc.status == "FAILED"


@pytest.mark.asyncio
async def test_process_document_parsing_error(db_session):
    """Test document processing when parsing fails"""
    from app.db.models import Document, Tenant
    
    tenant = Tenant(name="test_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        title="corrupt.pdf",
        content_hash="hash123",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        with patch("app.events.consumer.parser") as mock_parser:
            mock_get_file.return_value = b"Corrupt PDF data"
            mock_parser.parse.side_effect = Exception("Parsing failed")
            
            await process_document(
                str(doc.id),
                "corrupt.pdf",
                str(tenant.id),
                "corrupt.pdf"
            )
    
    # Verify document status updated to FAILED
    await db_session.refresh(doc)
    assert doc.status == "FAILED"


@pytest.mark.asyncio
async def test_process_document_indexing_error(db_session):
    """Test document processing when Qdrant indexing fails"""
    from app.db.models import Document, Tenant
    
    tenant = Tenant(name="test_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        title="test.txt",
        content_hash="hash123",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        with patch("app.events.consumer.parser") as mock_parser:
            with patch("app.events.consumer.SemanticChunker") as mock_chunker_class:
                with patch("app.events.consumer.upsert_document_chunks_to_qdrant") as mock_upsert:
                    with patch("app.events.consumer.upload_file") as mock_upload:
                        mock_get_file.return_value = b"Test content"
                        mock_parser.parse.return_value = "Parsed text"
                        
                        mock_chunker = MagicMock()
                        mock_chunker.chunk_text.return_value = ["Chunk 1"]
                        mock_chunker_class.return_value = mock_chunker
                        
                        mock_upload.return_value = True
                        mock_upsert.side_effect = Exception("Qdrant connection error")
                        
                        await process_document(
                            str(doc.id),
                            "test.txt",
                            str(tenant.id),
                            "test.txt"
                        )
    
    # Verify document status updated to FAILED
    await db_session.refresh(doc)
    assert doc.status == "FAILED"


@pytest.mark.asyncio
async def test_process_document_nonexistent():
    """Test processing non-existent document"""
    fake_id = str(uuid.uuid4())
    
    # Should handle gracefully without raising exception
    await process_document(
        fake_id,
        "test.txt",
        str(uuid.uuid4()),
        "test.txt"
    )


@pytest.mark.asyncio
async def test_process_document_stores_parsed_chunks(db_session):
    """Test that parsed chunks are stored in MinIO"""
    from app.db.models import Document, Tenant
    
    tenant = Tenant(name="test_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        title="test.txt",
        content_hash="hash123",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        with patch("app.events.consumer.parser") as mock_parser:
            with patch("app.events.consumer.SemanticChunker") as mock_chunker_class:
                with patch("app.events.consumer.upsert_document_chunks_to_qdrant") as mock_upsert:
                    with patch("app.events.consumer.upload_file") as mock_upload:
                        mock_get_file.return_value = b"Test content"
                        mock_parser.parse.return_value = "Parsed text"
                        
                        mock_chunker = MagicMock()
                        mock_chunker.chunk_text.return_value = ["Chunk 1", "Chunk 2"]
                        mock_chunker_class.return_value = mock_chunker
                        
                        mock_upload.return_value = True
                        mock_upsert.return_value = None
                        
                        await process_document(
                            str(doc.id),
                            "test.txt",
                            str(tenant.id),
                            "test.txt"
                        )
                        
                        # Verify upload_file was called with parsed chunks
                        mock_upload.assert_called_once()
                        call_args = mock_upload.call_args
                        assert call_args[0][0] == "parsed-chunks"
                        assert call_args[0][1] == "test.json"
                        
                        # Verify JSON structure
                        uploaded_data = json.loads(call_args[0][2])
                        assert len(uploaded_data) == 2
                        assert uploaded_data[0]["chunk_index"] == 0
                        assert uploaded_data[0]["text"] == "Chunk 1"


@pytest.mark.asyncio
async def test_process_document_upload_failure_non_fatal(db_session):
    """Test that MinIO upload failure doesn't fail document processing"""
    from app.db.models import Document, Tenant
    
    tenant = Tenant(name="test_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        title="test.txt",
        content_hash="hash123",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        with patch("app.events.consumer.parser") as mock_parser:
            with patch("app.events.consumer.SemanticChunker") as mock_chunker_class:
                with patch("app.events.consumer.upsert_document_chunks_to_qdrant") as mock_upsert:
                    with patch("app.events.consumer.upload_file") as mock_upload:
                        mock_get_file.return_value = b"Test content"
                        mock_parser.parse.return_value = "Parsed text"
                        
                        mock_chunker = MagicMock()
                        mock_chunker.chunk_text.return_value = ["Chunk 1"]
                        mock_chunker_class.return_value = mock_chunker
                        
                        mock_upload.return_value = False  # Upload fails
                        mock_upsert.return_value = None
                        
                        await process_document(
                            str(doc.id),
                            "test.txt",
                            str(tenant.id),
                            "test.txt"
                        )
    
    # Document should still be READY despite upload failure
    await db_session.refresh(doc)
    assert doc.status == "READY"


@pytest.mark.asyncio
async def test_process_document_chunker_parameters(db_session):
    """Test that chunker is initialized with correct parameters"""
    from app.db.models import Document, Tenant
    
    tenant = Tenant(name="test_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    doc = Document(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        title="test.txt",
        content_hash="hash123",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        with patch("app.events.consumer.parser") as mock_parser:
            with patch("app.events.consumer.SemanticChunker") as mock_chunker_class:
                with patch("app.events.consumer.upsert_document_chunks_to_qdrant") as mock_upsert:
                    with patch("app.events.consumer.upload_file") as mock_upload:
                        mock_get_file.return_value = b"Test content"
                        mock_parser.parse.return_value = "Parsed text"
                        
                        mock_chunker = MagicMock()
                        mock_chunker.chunk_text.return_value = ["Chunk 1"]
                        mock_chunker_class.return_value = mock_chunker
                        
                        mock_upload.return_value = True
                        mock_upsert.return_value = None
                        
                        await process_document(
                            str(doc.id),
                            "test.txt",
                            str(tenant.id),
                            "test.txt"
                        )
                        
                        # Verify chunker initialized with correct parameters
                        mock_chunker_class.assert_called_once_with(chunk_size=512, overlap=64)

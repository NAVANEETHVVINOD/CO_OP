"""Enhanced tests for document indexer service."""
import pytest
import uuid
from unittest.mock import AsyncMock, patch
from app.services.indexer import upsert_document_chunks_to_qdrant


@pytest.mark.asyncio
async def test_upsert_empty_chunks():
    """Test upserting empty chunks list"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    
    # Should return early without calling Qdrant
    with patch("app.services.indexer.qdrant") as mock_qdrant:
        await upsert_document_chunks_to_qdrant(tenant_id, document_id, [])
        
        # Should not call upsert
        mock_qdrant.upsert.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_single_chunk():
    """Test upserting a single chunk"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = ["This is a test document chunk."]
    
    with patch("app.services.indexer.qdrant") as mock_qdrant:
        with patch("app.services.indexer.embedder") as mock_embedder:
            with patch("app.services.indexer.bm25_encoder") as mock_bm25:
                # Mock embeddings - use AsyncMock for async function
                mock_embedder.embed_batch = AsyncMock(return_value=[[0.1] * 384])
                mock_bm25.encode.return_value = ([1, 2, 3], [0.5, 0.3, 0.2])
                mock_qdrant.upsert = AsyncMock()
                
                await upsert_document_chunks_to_qdrant(tenant_id, document_id, chunks)
                
                # Should call embed_batch once
                mock_embedder.embed_batch.assert_called_once_with(chunks)
                
                # Should call BM25 encode once
                mock_bm25.encode.assert_called_once_with(chunks[0])
                
                # Should call upsert once
                mock_qdrant.upsert.assert_called_once()
                call_args = mock_qdrant.upsert.call_args
                assert call_args[1]["wait"] is True
                assert len(call_args[1]["points"]) == 1


@pytest.mark.asyncio
async def test_upsert_multiple_chunks():
    """Test upserting multiple chunks"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = [
        "First chunk of text.",
        "Second chunk of text.",
        "Third chunk of text."
    ]
    
    with patch("app.services.indexer.qdrant") as mock_qdrant:
        with patch("app.services.indexer.embedder") as mock_embedder:
            with patch("app.services.indexer.bm25_encoder") as mock_bm25:
                # Mock embeddings - use AsyncMock for async function
                mock_embedder.embed_batch = AsyncMock(return_value=[
                    [0.1] * 384,
                    [0.2] * 384,
                    [0.3] * 384
                ])
                mock_bm25.encode.return_value = ([1, 2, 3], [0.5, 0.3, 0.2])
                mock_qdrant.upsert = AsyncMock()
                
                await upsert_document_chunks_to_qdrant(tenant_id, document_id, chunks)
                
                # Should call embed_batch with all chunks
                mock_embedder.embed_batch.assert_called_once_with(chunks)
                
                # Should call BM25 encode for each chunk
                assert mock_bm25.encode.call_count == 3
                
                # Should call upsert with all points
                mock_qdrant.upsert.assert_called_once()
                call_args = mock_qdrant.upsert.call_args
                assert len(call_args[1]["points"]) == 3


@pytest.mark.asyncio
async def test_upsert_point_structure():
    """Test that upserted points have correct structure"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = ["Test chunk"]
    
    with patch("app.services.indexer.qdrant") as mock_qdrant:
        with patch("app.services.indexer.embedder") as mock_embedder:
            with patch("app.services.indexer.bm25_encoder") as mock_bm25:
                mock_embedder.embed_batch = AsyncMock(return_value=[[0.1] * 384])
                mock_bm25.encode.return_value = ([1, 2, 3], [0.5, 0.3, 0.2])
                mock_qdrant.upsert = AsyncMock()
                
                await upsert_document_chunks_to_qdrant(tenant_id, document_id, chunks)
                
                call_args = mock_qdrant.upsert.call_args
                point = call_args[1]["points"][0]
                
                # Check point structure
                assert hasattr(point, "id")
                assert hasattr(point, "vector")
                assert hasattr(point, "payload")
                
                # Check vector structure
                assert "dense" in point.vector
                assert "sparse" in point.vector
                # SparseVector is an object with attributes, not a dict
                assert hasattr(point.vector["sparse"], "indices")
                assert hasattr(point.vector["sparse"], "values")
                assert point.vector["sparse"].indices == [1, 2, 3]
                assert point.vector["sparse"].values == [0.5, 0.3, 0.2]
                
                # Check payload
                assert point.payload["tenant_id"] == str(tenant_id)
                assert point.payload["document_id"] == str(document_id)
                assert point.payload["chunk_index"] == 0
                assert point.payload["text"] == "Test chunk"


@pytest.mark.asyncio
async def test_upsert_chunk_indices():
    """Test that chunk indices are correctly assigned"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = ["Chunk 0", "Chunk 1", "Chunk 2"]
    
    with patch("app.services.indexer.qdrant") as mock_qdrant:
        with patch("app.services.indexer.embedder") as mock_embedder:
            with patch("app.services.indexer.bm25_encoder") as mock_bm25:
                mock_embedder.embed_batch = AsyncMock(return_value=[[0.1] * 384] * 3)
                mock_bm25.encode.return_value = ([1, 2], [0.5, 0.5])
                mock_qdrant.upsert = AsyncMock()
                
                await upsert_document_chunks_to_qdrant(tenant_id, document_id, chunks)
                
                call_args = mock_qdrant.upsert.call_args
                points = call_args[1]["points"]
                
                # Check chunk indices
                for i, point in enumerate(points):
                    assert point.payload["chunk_index"] == i
                    assert point.payload["text"] == f"Chunk {i}"


@pytest.mark.asyncio
async def test_upsert_with_qdrant_disabled():
    """Test upserting when Qdrant is disabled"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = ["Test chunk"]
    
    with patch("app.services.indexer.qdrant", None):
        # Should return early without error
        await upsert_document_chunks_to_qdrant(tenant_id, document_id, chunks)


@pytest.mark.asyncio
async def test_upsert_large_batch():
    """Test upserting large batch of chunks"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = [f"Chunk {i}" for i in range(100)]
    
    with patch("app.services.indexer.qdrant") as mock_qdrant:
        with patch("app.services.indexer.embedder") as mock_embedder:
            with patch("app.services.indexer.bm25_encoder") as mock_bm25:
                mock_embedder.embed_batch = AsyncMock(return_value=[[0.1] * 384] * 100)
                mock_bm25.encode.return_value = ([1, 2], [0.5, 0.5])
                mock_qdrant.upsert = AsyncMock()
                
                await upsert_document_chunks_to_qdrant(tenant_id, document_id, chunks)
                
                # Should handle large batch
                call_args = mock_qdrant.upsert.call_args
                assert len(call_args[1]["points"]) == 100


@pytest.mark.asyncio
async def test_upsert_with_special_characters():
    """Test upserting chunks with special characters"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = [
        "Text with émojis 🚀",
        "Text with quotes \"test\"",
        "Text with newlines\n\ntest"
    ]
    
    with patch("app.services.indexer.qdrant") as mock_qdrant:
        with patch("app.services.indexer.embedder") as mock_embedder:
            with patch("app.services.indexer.bm25_encoder") as mock_bm25:
                mock_embedder.embed_batch = AsyncMock(return_value=[[0.1] * 384] * 3)
                mock_bm25.encode.return_value = ([1], [0.5])
                mock_qdrant.upsert = AsyncMock()
                
                await upsert_document_chunks_to_qdrant(tenant_id, document_id, chunks)
                
                # Should handle special characters
                call_args = mock_qdrant.upsert.call_args
                points = call_args[1]["points"]
                assert len(points) == 3


@pytest.mark.asyncio
async def test_upsert_collection_name():
    """Test that upsert uses correct collection name"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = ["Test"]
    
    with patch("app.services.indexer.qdrant") as mock_qdrant:
        with patch("app.services.indexer.embedder") as mock_embedder:
            with patch("app.services.indexer.bm25_encoder") as mock_bm25:
                with patch("app.services.indexer.COLLECTION_NAME", "test-collection"):
                    mock_embedder.embed_batch = AsyncMock(return_value=[[0.1] * 384])
                    mock_bm25.encode.return_value = ([1], [0.5])
                    mock_qdrant.upsert = AsyncMock()
                    
                    await upsert_document_chunks_to_qdrant(tenant_id, document_id, chunks)
                    
                    call_args = mock_qdrant.upsert.call_args
                    assert call_args[1]["collection_name"] == "test-collection"


@pytest.mark.asyncio
async def test_upsert_wait_parameter():
    """Test that upsert waits for indexing to complete"""
    tenant_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunks = ["Test"]
    
    with patch("app.services.indexer.qdrant") as mock_qdrant:
        with patch("app.services.indexer.embedder") as mock_embedder:
            with patch("app.services.indexer.bm25_encoder") as mock_bm25:
                mock_embedder.embed_batch = AsyncMock(return_value=[[0.1] * 384])
                mock_bm25.encode.return_value = ([1], [0.5])
                mock_qdrant.upsert = AsyncMock()
                
                await upsert_document_chunks_to_qdrant(tenant_id, document_id, chunks)
                
                call_args = mock_qdrant.upsert.call_args
                assert call_args[1]["wait"] is True

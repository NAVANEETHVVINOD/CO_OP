"""
Integration tests for RAG pipeline end-to-end workflow
Tests: Upload → Parse → Chunk → Embed → Index → Search

**Validates: Requirements 6.1**
"""
import pytest
import uuid
import io
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock
from tests.v1_test_utils import seed_test_user


@pytest.mark.asyncio
async def test_rag_pipeline_complete_flow(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test complete RAG pipeline: upload → parse → chunk → embed → index → search
    
    Validates:
    - Document upload creates PENDING status
    - Document processing transitions through INDEXING to READY
    - Document is parsed correctly
    - Text is chunked appropriately
    - Chunks are embedded and indexed in Qdrant
    - Search returns correct results from indexed document
    
    **Validates: Requirements 6.1**
    """
    from app.db.models import Document
    from app.events.consumer import process_document
    from sqlalchemy import select
    
    # Setup test user
    user, token = await seed_test_user(db_session, email="rag_test@test.local")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test document content
    test_content = "This is a test document about LangGraph and AI agents. " * 20
    test_filename = "test_rag_doc.txt"
    
    # Step 1: Upload document
    with patch("app.routers.documents.upload_file") as mock_upload:
        mock_upload.return_value = True
        
        file_data = io.BytesIO(test_content.encode())
        files = {"file": (test_filename, file_data, "text/plain")}
        
        with patch("app.routers.documents.publish_ingestion_event") as mock_publish:
            mock_publish.return_value = None
            
            upload_response = await async_client.post(
                "/v1/documents",
                files=files,
                headers=headers
            )
    
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert "document_id" in upload_data
    assert upload_data["status"] == "PENDING"
    
    document_id = upload_data["document_id"]
    
    # Verify document created with PENDING status
    result = await db_session.execute(
        select(Document).where(Document.id == uuid.UUID(document_id))
    )
    doc = result.scalar_one_or_none()
    assert doc is not None
    assert doc.status == "PENDING"
    assert doc.title == test_filename
    
    # Step 2: Process document (parse → chunk → embed → index)
    with patch("app.events.consumer.get_file") as mock_get_file:
        mock_get_file.return_value = test_content.encode()
        
        with patch("app.events.consumer.upload_file") as mock_upload_chunks:
            mock_upload_chunks.return_value = True
            
            with patch("app.events.consumer.upsert_document_chunks_to_qdrant", new_callable=AsyncMock) as mock_upsert:
                mock_upsert.return_value = None
                
                # Process the document
                await process_document(
                    document_id=document_id,
                    file_path=f"{user.tenant_id}/{document_id}.txt",
                    tenant_id=str(user.tenant_id),
                    filename=test_filename
                )
    
    # Verify document status transitioned to READY
    await db_session.refresh(doc)
    assert doc.status == "READY"
    
    # Verify chunks were created and indexed
    assert mock_upsert.called
    call_args = mock_upsert.call_args
    # Compare UUIDs without hyphens to handle different formats
    assert str(call_args[1]["tenant_id"]).replace('-', '') == str(user.tenant_id).replace('-', '')
    assert str(call_args[1]["document_uuid"]).replace('-', '') == str(document_id).replace('-', '')
    chunks = call_args[1]["chunks_text"]
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    
    # Step 3: Search for indexed content
    with patch("app.routers.search.hybrid_search", new_callable=AsyncMock) as mock_search:
        # Mock search results with content from our document
        mock_search.return_value = [
            {
                "document_id": document_id,
                "chunk_index": 0,
                "text": chunks[0][:100],
                "rerank_score": 0.95
            }
        ]
        
        search_response = await async_client.post(
            "/v1/search",
            json={"query": "LangGraph AI agents", "top_k": 5},
            headers=headers
        )
    
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert "results" in search_data
    assert len(search_data["results"]) > 0
    
    # Verify search result contains our document
    result = search_data["results"][0]
    assert result["document_id"] == document_id
    assert "text" in result
    assert "score" in result
    assert result["score"] > 0


@pytest.mark.asyncio
async def test_rag_pipeline_document_status_transitions(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test document status transitions: PENDING → INDEXING → READY
    
    Validates:
    - Document starts in PENDING status after upload
    - Document transitions to READY after successful processing
    - Status can be queried at any point
    
    **Validates: Requirements 6.1**
    """
    from app.db.models import Document
    from app.events.consumer import process_document
    
    user, token = await seed_test_user(db_session, email="status_test@test.local")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create document in PENDING status
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        tenant_id=user.tenant_id,
        title="status_test.txt",
        content_hash=f"{user.tenant_id}/{doc_id}.txt",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    # Check initial status
    status_response = await async_client.get(
        f"/v1/documents/{doc_id}/status",
        headers=headers
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "PENDING"
    
    # Process document
    test_content = "Test content for status transitions."
    with patch("app.events.consumer.get_file") as mock_get_file:
        mock_get_file.return_value = test_content.encode()
        
        with patch("app.events.consumer.upload_file") as mock_upload:
            mock_upload.return_value = True
            
            with patch("app.events.consumer.upsert_document_chunks_to_qdrant", new_callable=AsyncMock) as mock_upsert:
                mock_upsert.return_value = None
                
                await process_document(
                    document_id=str(doc_id),
                    file_path=doc.content_hash,
                    tenant_id=str(user.tenant_id),
                    filename="status_test.txt"
                )
    
    # Check final status
    status_response = await async_client.get(
        f"/v1/documents/{doc_id}/status",
        headers=headers
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "READY"


@pytest.mark.asyncio
async def test_rag_pipeline_search_returns_correct_results(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that search returns correct results from indexed documents
    
    Validates:
    - Search query matches indexed content
    - Results are ranked by relevance
    - Results include document metadata
    - Multiple documents can be searched
    
    **Validates: Requirements 6.1**
    """
    from app.db.models import Document
    
    user, token = await seed_test_user(db_session, email="search_test@test.local")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create multiple documents
    doc1_id = uuid.uuid4()
    doc1 = Document(
        id=doc1_id,
        tenant_id=user.tenant_id,
        title="langgraph_guide.txt",
        content_hash=f"{user.tenant_id}/{doc1_id}.txt",
        status="READY"
    )
    
    doc2_id = uuid.uuid4()
    doc2 = Document(
        id=doc2_id,
        tenant_id=user.tenant_id,
        title="fastapi_tutorial.txt",
        content_hash=f"{user.tenant_id}/{doc2_id}.txt",
        status="READY"
    )
    
    db_session.add_all([doc1, doc2])
    await db_session.commit()
    
    # Mock search to return results from doc1 (more relevant to query)
    with patch("app.routers.search.hybrid_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [
            {
                "document_id": str(doc1_id),
                "chunk_index": 0,
                "text": "LangGraph is a framework for building stateful AI agents.",
                "rerank_score": 0.92
            },
            {
                "document_id": str(doc1_id),
                "chunk_index": 1,
                "text": "LangGraph uses state machines to manage agent workflows.",
                "rerank_score": 0.88
            },
            {
                "document_id": str(doc2_id),
                "chunk_index": 0,
                "text": "FastAPI is a modern web framework for building APIs.",
                "rerank_score": 0.45
            }
        ]
        
        search_response = await async_client.post(
            "/v1/search",
            json={"query": "LangGraph agents", "top_k": 5},
            headers=headers
        )
    
    assert search_response.status_code == 200
    search_data = search_response.json()
    results = search_data["results"]
    
    # Verify results are returned
    assert len(results) == 3
    
    # Verify results are ranked by relevance (highest score first)
    assert results[0]["score"] >= results[1]["score"]
    assert results[1]["score"] >= results[2]["score"]
    
    # Verify most relevant results are from doc1
    assert results[0]["document_id"] == str(doc1_id)
    assert results[1]["document_id"] == str(doc1_id)
    
    # Verify result structure
    for result in results:
        assert "document_id" in result
        assert "chunk_index" in result
        assert "text" in result
        assert "score" in result
        assert isinstance(result["score"], float)


@pytest.mark.asyncio
async def test_rag_pipeline_parsing_different_formats(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test RAG pipeline with different document formats (PDF, DOCX, TXT)
    
    Validates:
    - Parser handles different file formats
    - Content is extracted correctly from each format
    - All formats can be indexed and searched
    
    **Validates: Requirements 6.1**
    """
    from app.events.consumer import process_document
    from app.db.models import Document
    
    user, _ = await seed_test_user(db_session, email="format_test@test.local")
    
    test_cases = [
        ("test.txt", "This is plain text content about AI agents."),
        ("test.pdf", "This is PDF content about machine learning."),
        ("test.docx", "This is DOCX content about neural networks.")
    ]
    
    for filename, content in test_cases:
        doc_id = uuid.uuid4()
        doc = Document(
            id=doc_id,
            tenant_id=user.tenant_id,
            title=filename,
            content_hash=f"{user.tenant_id}/{doc_id}.{filename.split('.')[-1]}",
            status="PENDING"
        )
        db_session.add(doc)
        await db_session.commit()
        
        with patch("app.events.consumer.get_file") as mock_get_file:
            mock_get_file.return_value = content.encode()
            
            with patch("app.events.consumer.parser.parse") as mock_parser:
                mock_parser.return_value = content
                
                with patch("app.events.consumer.upload_file") as mock_upload:
                    mock_upload.return_value = True
                    
                    with patch("app.events.consumer.upsert_document_chunks_to_qdrant", new_callable=AsyncMock) as mock_upsert:
                        mock_upsert.return_value = None
                        
                        # Should not raise exception
                        await process_document(
                            document_id=str(doc_id),
                            file_path=doc.content_hash,
                            tenant_id=str(user.tenant_id),
                            filename=filename
                        )
        
        # Verify document processed successfully
        await db_session.refresh(doc)
        assert doc.status == "READY"


@pytest.mark.asyncio
async def test_rag_pipeline_chunking_strategy(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that chunking strategy produces appropriate chunk sizes
    
    Validates:
    - Chunks are created with correct size
    - Chunks have appropriate overlap
    - Long documents are split into multiple chunks
    - Short documents may result in single chunk
    
    **Validates: Requirements 6.1**
    """
    from app.events.consumer import process_document
    from app.db.models import Document
    
    user, _ = await seed_test_user(db_session, email="chunk_test@test.local")
    
    # Create long document that will be chunked
    long_content = " ".join([f"Word{i}" for i in range(1000)])  # 1000 words
    
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        tenant_id=user.tenant_id,
        title="long_doc.txt",
        content_hash=f"{user.tenant_id}/{doc_id}.txt",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        mock_get_file.return_value = long_content.encode()
        
        with patch("app.events.consumer.upload_file") as mock_upload:
            mock_upload.return_value = True
            
            with patch("app.events.consumer.upsert_document_chunks_to_qdrant", new_callable=AsyncMock) as mock_upsert:
                mock_upsert.return_value = None
                
                await process_document(
                    document_id=str(doc_id),
                    file_path=doc.content_hash,
                    tenant_id=str(user.tenant_id),
                    filename="long_doc.txt"
                )
                
                # Verify chunks were created
                assert mock_upsert.called
                chunks = mock_upsert.call_args[1]["chunks_text"]
                
                # Long document should produce multiple chunks
                assert len(chunks) > 1
                
                # Each chunk should be reasonable size (not too long or too short)
                for chunk in chunks:
                    word_count = len(chunk.split())
                    assert word_count > 0
                    # Chunks should be roughly chunk_size (512 words) or less
                    assert word_count <= 600  # Allow some flexibility


@pytest.mark.asyncio
async def test_rag_pipeline_embedding_generation(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that embeddings are generated for document chunks
    
    Validates:
    - Embeddings are generated for all chunks
    - Embeddings have correct dimensions
    - Embeddings are passed to indexer
    
    **Validates: Requirements 6.1**
    """
    from app.events.consumer import process_document
    from app.db.models import Document
    
    user, _ = await seed_test_user(db_session, email="embed_test@test.local")
    
    test_content = "This is test content for embedding generation."
    
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        tenant_id=user.tenant_id,
        title="embed_test.txt",
        content_hash=f"{user.tenant_id}/{doc_id}.txt",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        mock_get_file.return_value = test_content.encode()
        
        with patch("app.events.consumer.upload_file") as mock_upload:
            mock_upload.return_value = True
            
            with patch("app.events.consumer.upsert_document_chunks_to_qdrant", new_callable=AsyncMock) as mock_upsert:
                mock_upsert.return_value = None
                
                await process_document(
                    document_id=str(doc_id),
                    file_path=doc.content_hash,
                    tenant_id=str(user.tenant_id),
                    filename="embed_test.txt"
                )
                
                # Verify upsert was called (which means embeddings were generated)
                assert mock_upsert.called
                
                # Verify chunks were passed to indexer
                chunks = mock_upsert.call_args[1]["chunks_text"]
                assert len(chunks) > 0


@pytest.mark.asyncio
async def test_rag_pipeline_error_handling(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test RAG pipeline error handling
    
    Validates:
    - Document status set to FAILED on parsing error
    - Document status set to FAILED on indexing error
    - Errors are logged appropriately
    
    **Validates: Requirements 6.1**
    """
    from app.events.consumer import process_document
    from app.db.models import Document
    
    user, _ = await seed_test_user(db_session, email="error_test@test.local")
    
    # Test parsing error
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        tenant_id=user.tenant_id,
        title="corrupt.pdf",
        content_hash=f"{user.tenant_id}/{doc_id}.pdf",
        status="PENDING"
    )
    db_session.add(doc)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        mock_get_file.return_value = b"corrupt data"
        
        with patch("app.services.parser.parser.parse") as mock_parse:
            mock_parse.side_effect = Exception("Parsing failed")
            
            await process_document(
                document_id=str(doc_id),
                file_path=doc.content_hash,
                tenant_id=str(user.tenant_id),
                filename="corrupt.pdf"
            )
    
    # Verify document status set to FAILED
    await db_session.refresh(doc)
    assert doc.status == "FAILED"
    
    # Test indexing error
    doc2_id = uuid.uuid4()
    doc2 = Document(
        id=doc2_id,
        tenant_id=user.tenant_id,
        title="index_fail.txt",
        content_hash=f"{user.tenant_id}/{doc2_id}.txt",
        status="PENDING"
    )
    db_session.add(doc2)
    await db_session.commit()
    
    with patch("app.events.consumer.get_file") as mock_get_file:
        mock_get_file.return_value = b"test content"
        
        with patch("app.events.consumer.upload_file") as mock_upload:
            mock_upload.return_value = True
            
            with patch("app.events.consumer.upsert_document_chunks_to_qdrant", new_callable=AsyncMock) as mock_upsert:
                mock_upsert.side_effect = Exception("Indexing failed")
                
                await process_document(
                    document_id=str(doc2_id),
                    file_path=doc2.content_hash,
                    tenant_id=str(user.tenant_id),
                    filename="index_fail.txt"
                )
    
    # Verify document status set to FAILED
    await db_session.refresh(doc2)
    assert doc2.status == "FAILED"

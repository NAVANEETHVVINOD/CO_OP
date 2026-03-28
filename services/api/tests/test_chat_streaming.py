"""
Integration tests for complete chat streaming workflow.

Tests the full chat streaming workflow:
- Query submission
- Document retrieval
- Reranking
- Answer generation
- SSE stream events (citations, tokens, done)

**Validates: Requirements 6.3**
"""
import pytest
import json
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.v1_test_utils import seed_test_user


# Mock LangGraph research agent response
async def mock_research_agent_full_pipeline(*args, **kwargs):
    """
    Mock the complete RAG pipeline: retrieve → rerank → generate
    
    Returns realistic data structure matching the actual LangGraph agent output.
    """
    return {
        "tenant_id": kwargs.get("tenant_id", "test-tenant"),
        "question": kwargs.get("question", "Test question"),
        "chat_history": kwargs.get("chat_history", []),
        "retrieved_docs": [
            {"document_id": "doc1", "text": "Retrieved content 1", "score": 0.85},
            {"document_id": "doc2", "text": "Retrieved content 2", "score": 0.78},
            {"document_id": "doc3", "text": "Retrieved content 3", "score": 0.72},
        ],
        "reranked_docs": [
            {
                "document_id": "doc1",
                "chunk_index": 0,
                "text": "Reranked content 1",
                "rerank_score": 0.95,
                "rrf_score": 0.90
            },
            {
                "document_id": "doc2",
                "chunk_index": 1,
                "text": "Reranked content 2",
                "rerank_score": 0.88,
                "rrf_score": 0.82
            },
            {
                "document_id": "doc3",
                "chunk_index": 0,
                "text": "Reranked content 3",
                "rerank_score": 0.81,
                "rrf_score": 0.75
            },
        ],
        "final_answer": "This is the generated answer based on retrieved documents."
    }


@pytest.mark.asyncio
async def test_complete_chat_streaming_flow(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test complete chat streaming flow: query → retrieve → rerank → generate → SSE stream
    
    This integration test validates the entire chat workflow:
    1. User submits query with authentication
    2. System retrieves relevant documents
    3. System reranks documents for relevance
    4. System generates answer using LLM
    5. System streams response via SSE with proper event ordering
    """
    user, token = await seed_test_user(db_session, email="chatstream@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_research_agent_full_pipeline):
        # Submit chat query and stream response
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={
                "message": "What is the Co-Op system?",
                "history": [],
                "conversation_id": None
            },
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200, "Chat stream should return 200 OK"
            assert response.headers["content-type"] == "text/event-stream", "Response should be SSE stream"
            
            # Read full stream
            content = await response.aread()
            stream_text = content.decode('utf-8')
            
            # Validate stream contains all expected event types
            assert 'event: citation' in stream_text, "Stream should contain citation events"
            assert 'event: token' in stream_text, "Stream should contain token events"
            assert 'event: done' in stream_text, "Stream should contain done event"
            
            # Validate citation data structure
            assert '"source":' in stream_text, "Citations should include source field"
            assert '"chunk_index":' in stream_text, "Citations should include chunk_index field"
            assert '"score":' in stream_text, "Citations should include score field"
            
            # Validate token data structure
            assert '"content":' in stream_text, "Tokens should include content field"
            
            # Validate done event data structure
            assert '"conversation_id":' in stream_text, "Done event should include conversation_id"
            assert '"total_chunks":' in stream_text, "Done event should include total_chunks"


@pytest.mark.asyncio
async def test_citation_events_sent_before_tokens(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that citation events are sent before token events in SSE stream.
    
    This is critical for UI to display sources before streaming the answer.
    """
    user, token = await seed_test_user(db_session, email="citation_order@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_research_agent_full_pipeline):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Test query", "history": []},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            
            content = await response.aread()
            stream_text = content.decode('utf-8')
            
            # Find positions of first citation and first token
            first_citation_pos = stream_text.find('event: citation')
            first_token_pos = stream_text.find('event: token')
            
            assert first_citation_pos != -1, "Stream should contain citation events"
            assert first_token_pos != -1, "Stream should contain token events"
            assert first_citation_pos < first_token_pos, "Citations MUST be sent before tokens"


@pytest.mark.asyncio
async def test_done_event_sent_at_end(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that done event is sent at the end of the stream.
    
    The done event signals completion and includes metadata like conversation_id.
    """
    user, token = await seed_test_user(db_session, email="done_event@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_research_agent_full_pipeline):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Test query", "history": []},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            
            content = await response.aread()
            stream_text = content.decode('utf-8')
            
            # Find positions of last token and done event
            last_token_pos = stream_text.rfind('event: token')
            done_pos = stream_text.find('event: done')
            
            assert done_pos != -1, "Stream should contain done event"
            assert last_token_pos < done_pos, "Done event MUST be sent after all tokens"
            
            # Validate done event contains required fields
            # Extract done event data
            done_start = stream_text.find('event: done')
            done_data_start = stream_text.find('data:', done_start)
            done_data_end = stream_text.find('\n', done_data_start)
            done_data_str = stream_text[done_data_start + 5:done_data_end].strip()
            
            done_data = json.loads(done_data_str)
            assert "conversation_id" in done_data, "Done event should include conversation_id"
            assert "total_chunks" in done_data, "Done event should include total_chunks"


@pytest.mark.asyncio
async def test_chat_streaming_with_conversation_history(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test chat streaming with conversation history for context.
    """
    user, token = await seed_test_user(db_session, email="history@test.local")
    
    conversation_history = [
        {"role": "user", "content": "What is Co-Op?"},
        {"role": "assistant", "content": "Co-Op is an enterprise AI operating system."},
    ]
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_research_agent_full_pipeline):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={
                "message": "Tell me more about its features",
                "history": conversation_history,
                "conversation_id": "test-conv-123"
            },
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            
            content = await response.aread()
            stream_text = content.decode('utf-8')
            
            assert 'event: citation' in stream_text
            assert 'event: token' in stream_text
            assert 'event: done' in stream_text


@pytest.mark.asyncio
async def test_chat_streaming_requires_authentication(async_client: AsyncClient):
    """
    Test that chat streaming endpoint requires valid authentication.
    """
    # Test without authentication
    response = await async_client.post(
        "/v1/chat/stream",
        json={"message": "Test query"}
    )
    assert response.status_code == 401, "Chat stream should require authentication"


@pytest.mark.asyncio
async def test_chat_streaming_rejects_empty_message(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that chat streaming rejects empty messages.
    """
    user, token = await seed_test_user(db_session, email="empty_msg@test.local")
    
    response = await async_client.post(
        "/v1/chat/stream",
        json={"message": "", "history": []},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400, "Chat stream should reject empty messages"
    assert "empty" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_chat_streaming_citation_data_structure(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that citation events contain all required fields with correct data types.
    """
    user, token = await seed_test_user(db_session, email="citation_data@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_research_agent_full_pipeline):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Test query", "history": []},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            
            content = await response.aread()
            stream_text = content.decode('utf-8')
            
            # Extract first citation event
            citation_start = stream_text.find('event: citation')
            assert citation_start != -1, "Stream should contain citation events"
            
            # Find the data line after the citation event
            data_start = stream_text.find('data:', citation_start)
            data_end = stream_text.find('\n', data_start)
            citation_data_str = stream_text[data_start + 5:data_end].strip()
            
            # Parse citation JSON
            citation_data = json.loads(citation_data_str)
            
            # Validate citation structure
            assert "source" in citation_data, "Citation should include source"
            assert "chunk_index" in citation_data, "Citation should include chunk_index"
            assert "page" in citation_data, "Citation should include page"
            assert "score" in citation_data, "Citation should include score"
            
            # Validate data types
            assert isinstance(citation_data["source"], str), "Source should be string"
            assert isinstance(citation_data["chunk_index"], int), "Chunk index should be integer"
            assert isinstance(citation_data["page"], int), "Page should be integer"
            assert isinstance(citation_data["score"], (int, float)), "Score should be numeric"


@pytest.mark.asyncio
async def test_chat_streaming_token_data_structure(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that token events contain content field with string data.
    """
    user, token = await seed_test_user(db_session, email="token_data@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_research_agent_full_pipeline):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Test query", "history": []},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            
            content = await response.aread()
            stream_text = content.decode('utf-8')
            
            # Extract first token event
            token_start = stream_text.find('event: token')
            assert token_start != -1, "Stream should contain token events"
            
            # Find the data line after the token event
            data_start = stream_text.find('data:', token_start)
            data_end = stream_text.find('\n', data_start)
            token_data_str = stream_text[data_start + 5:data_end].strip()
            
            # Parse token JSON
            token_data = json.loads(token_data_str)
            
            # Validate token structure
            assert "content" in token_data, "Token should include content field"
            assert isinstance(token_data["content"], str), "Content should be string"


@pytest.mark.asyncio
async def test_chat_streaming_multiple_citations(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that multiple citation events are sent for multiple reranked documents.
    """
    user, token = await seed_test_user(db_session, email="multi_citation@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_research_agent_full_pipeline):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Test query", "history": []},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            
            content = await response.aread()
            stream_text = content.decode('utf-8')
            
            # Count citation events
            citation_count = stream_text.count('event: citation')
            
            # Should have multiple citations (up to 5 from reranked docs)
            assert citation_count >= 3, f"Should have at least 3 citation events, got {citation_count}"
            assert citation_count <= 5, f"Should have at most 5 citation events, got {citation_count}"


@pytest.mark.asyncio
async def test_chat_streaming_error_handling(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that chat streaming handles errors gracefully and sends error in stream.
    """
    user, token = await seed_test_user(db_session, email="error_handling@test.local")
    
    # Mock agent to raise an exception
    async def mock_agent_error(*args, **kwargs):
        raise Exception("Simulated agent error")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_agent_error):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Test query", "history": []},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200, "Stream should start even if agent fails"
            
            content = await response.aread()
            stream_text = content.decode('utf-8')
            
            # Should contain error message in token event
            assert 'Error:' in stream_text or 'error' in stream_text.lower(), "Stream should contain error message"
            
            # Should still send done event
            assert 'event: done' in stream_text, "Stream should send done event even on error"


@pytest.mark.asyncio
async def test_chat_streaming_sse_format_compliance(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that SSE stream follows proper Server-Sent Events format.
    
    SSE format requirements:
    - event: <event_type>
    - data: <json_data>
    - Empty line between events
    """
    user, token = await seed_test_user(db_session, email="sse_format@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_research_agent_full_pipeline):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Test query", "history": []},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            
            content = await response.aread()
            stream_text = content.decode('utf-8')
            
            # Validate SSE format: each event should have "event:" and "data:" lines
            events = stream_text.split('event:')
            
            for event in events[1:]:  # Skip first empty split
                # Each event should have a data line
                assert 'data:' in event, "Each SSE event should have a data line"
                
                # Extract event type and data
                lines = event.strip().split('\n')
                event_type = lines[0].strip()
                
                # Validate event types
                assert event_type in ['citation', 'token', 'done'], f"Invalid event type: {event_type}"

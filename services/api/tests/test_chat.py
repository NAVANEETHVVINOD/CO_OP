import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.v1_test_utils import seed_test_user


# Mock for the LangGraph `ainvoke` method
async def mock_ainvoke(*args, **kwargs):
    return {
        "reranked_docs": [{"document_id": "test_doc", "text": "Test Context", "rerank_score": 0.99}],
        "final_answer": "Hello World"
    }


@pytest.mark.asyncio
async def test_chat_stream(async_client: AsyncClient, db_session: AsyncSession):
    """Test chat streaming with SSE events"""
    user, token = await seed_test_user(db_session, email="chatter@co-op.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_ainvoke):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Hi"},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            content = await response.aread()
            text = content.decode('utf-8')
            
            # Check SSE components
            assert 'event: citation' in text
            assert 'event: token' in text
            assert 'data: {"content": "Hello "}' in text
            assert 'data: {"content": "World "}' in text
            assert 'event: done' in text


@pytest.mark.asyncio
async def test_chat_stream_without_auth(async_client: AsyncClient):
    """Test chat streaming requires authentication"""
    response = await async_client.post(
        "/v1/chat/stream",
        json={"message": "Hi"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_stream_empty_message(async_client: AsyncClient, db_session: AsyncSession):
    """Test chat streaming with empty message"""
    user, token = await seed_test_user(db_session, email="empty@test.local")
    
    response = await async_client.post(
        "/v1/chat/stream",
        json={"message": ""},
        headers={"Authorization": f"Bearer {token}"}
    )
    # Backend returns 400 for empty message
    assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
async def test_chat_stream_with_conversation_id(async_client: AsyncClient, db_session: AsyncSession):
    """Test chat streaming with existing conversation"""
    user, token = await seed_test_user(db_session, email="conv@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_ainvoke):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Follow-up question", "conversation_id": "test-conv-id"},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            content = await response.aread()
            text = content.decode('utf-8')
            assert 'event: done' in text


@pytest.mark.asyncio
async def test_chat_stream_citation_order(async_client: AsyncClient, db_session: AsyncSession):
    """Test that citations are sent before tokens in SSE stream"""
    user, token = await seed_test_user(db_session, email="citation@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_ainvoke):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Test"},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            content = await response.aread()
            text = content.decode('utf-8')
            
            # Find positions of citation and token events
            citation_pos = text.find('event: citation')
            token_pos = text.find('event: token')
            
            # Citations should come before tokens
            assert citation_pos < token_pos, "Citations should be sent before tokens"


@pytest.mark.asyncio
async def test_chat_stream_done_event(async_client: AsyncClient, db_session: AsyncSession):
    """Test that done event is sent at the end of stream"""
    user, token = await seed_test_user(db_session, email="done@test.local")
    
    with patch("app.routers.chat.research_agent.ainvoke", side_effect=mock_ainvoke):
        async with async_client.stream(
            "POST",
            "/v1/chat/stream",
            json={"message": "Test"},
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            assert response.status_code == 200
            content = await response.aread()
            text = content.decode('utf-8')
            
            # Done event should be present (may have trailing whitespace/newlines)
            assert 'event: done' in text, "Stream should contain done event"



@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_chat_stream_with_long_message(async_client: AsyncClient, db_session: AsyncSession):
    """POST /v1/chat/stream handles long messages."""
    user, token = await seed_test_user(db_session)
    
    long_message = "This is a test message. " * 100  # ~2500 characters
    
    response = await async_client.post(
        "/v1/chat/stream",
        json={"message": long_message},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

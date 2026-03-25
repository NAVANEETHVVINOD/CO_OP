import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Tenant, User
from app.core.security import get_password_hash

# Mock for the LangGraph `ainvoke` method
async def mock_ainvoke(*args, **kwargs):
    return {
        "reranked_docs": [{"document_id": "test_doc", "text": "Test Context", "rerank_score": 0.99}],
        "final_answer": "Hello World"
    }

@pytest.mark.asyncio
async def test_chat_stream(async_client: AsyncClient, db_session: AsyncSession):
    # Setup test user
    tenant = Tenant(name="chat_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    user = User(
        tenant_id=tenant.id,
        email="chatter@co-op.local",
        hashed_password=get_password_hash("testpass")
    )
    db_session.add(user)
    await db_session.commit()
    
    auth_resp = await async_client.post(
        "/v1/auth/token",
        data={"username": "chatter@co-op.local", "password": "testpass"}
    )
    token = auth_resp.json()["access_token"]
    
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

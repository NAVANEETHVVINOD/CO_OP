import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Tenant, User
from app.core.security import get_password_hash

@pytest.mark.asyncio
async def test_search_endpoint(async_client: AsyncClient, db_session: AsyncSession):
    # Setup test user for token
    tenant = Tenant(name="search_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    user = User(
        tenant_id=tenant.id,
        email="searcher@co-op.local",
        hashed_password=get_password_hash("testpass")
    )
    db_session.add(user)
    await db_session.commit()
    
    auth_resp = await async_client.post(
        "/v1/auth/token",
        data={"username": "searcher@co-op.local", "password": "testpass"}
    )
    token = auth_resp.json()["access_token"]
    
    # Mock the hybrid_search to completely bypass Qdrant and deep ML models layer during tests
    mock_results = [
        {"document_id": "doc123", "chunk_index": 0, "text": "This is a dummy search result", "rerank_score": 0.99}
    ]
    with patch("app.routers.search.hybrid_search", return_value=mock_results):
        search_resp = await async_client.post(
            "/v1/search",
            json={"query": "dummy search", "top_k": 3},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert search_resp.status_code == 200
        data = search_resp.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["text"] == "This is a dummy search result"
        assert data["results"][0]["document_id"] == "doc123"
        assert data["results"][0]["score"] == 0.99

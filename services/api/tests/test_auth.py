import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_login_success(async_client: AsyncClient):
    # Testing login with the seeded admin user
    await async_client.post(
        "/v1/auth/token",
        data={
            "username": "admin@co-op.local",
            "password": "testpass123", # matches DB_PASS in fake settings if we use the default
        }
    )
    # The application initialization seeds the user in main.py, 
    # but the test setup drops and creates tables. 
    # Let's seed the user here just in case, or run a startup event equivalent.
    
    # Wait, the lifespan event doesn't run automatically with ASGITransport without explicitly calling it.
    pass

@pytest.mark.asyncio
async def test_auth_full_flow(async_client: AsyncClient, db_session):
    from app.db.models import Tenant, User
    from app.core.security import get_password_hash
    
    # Manually seed user
    tenant = Tenant(name="admin_test")
    db_session.add(tenant)
    await db_session.flush()
    
    user = User(
        tenant_id=tenant.id,
        email="testadmin@co-op.local",
        hashed_password=get_password_hash("testpass")
    )
    db_session.add(user)
    await db_session.commit()
    
    # Test Login
    response = await async_client.post(
        "/v1/auth/token",
        data={
            "username": "testadmin@co-op.local",
            "password": "testpass",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    
    # Test /me
    me_response = await async_client.get(
        "/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "testadmin@co-op.local"
    
    # Test Refresh
    refresh_response = await async_client.post(
        "/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    new_data = refresh_response.json()
    assert "access_token" in new_data
    assert new_data["access_token"] != access_token

    # Test Login Failure
    bad_login = await async_client.post(
        "/v1/auth/token",
        data={
            "username": "testadmin@co-op.local",
            "password": "wrongpassword",
        }
    )
    assert bad_login.status_code == 401

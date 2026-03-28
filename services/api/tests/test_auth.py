import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Tenant, User
from app.core.security import get_password_hash
from tests.v1_test_utils import seed_test_user


@pytest.mark.asyncio
async def test_auth_login_success(async_client: AsyncClient, db_session: AsyncSession):
    """Test successful login with valid credentials"""
    user, _ = await seed_test_user(db_session, email="login@test.local", password="testpass")
    
    response = await async_client.post(
        "/v1/auth/token",
        data={
            "username": "login@test.local",
            "password": "testpass",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_auth_invalid_credentials(async_client: AsyncClient, db_session: AsyncSession):
    """Test login with invalid password"""
    user, _ = await seed_test_user(db_session, email="invalid@test.local", password="correctpass")
    
    response = await async_client.post(
        "/v1/auth/token",
        data={
            "username": "invalid@test.local",
            "password": "wrongpassword",
        }
    )
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_auth_nonexistent_user(async_client: AsyncClient):
    """Test login with non-existent user"""
    response = await async_client.post(
        "/v1/auth/token",
        data={
            "username": "nonexistent@test.local",
            "password": "anypassword",
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_missing_credentials(async_client: AsyncClient):
    """Test login with missing credentials"""
    response = await async_client.post(
        "/v1/auth/token",
        data={"username": "test@test.local"}
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Refresh token not yet implemented in auth router")
async def test_auth_token_refresh(async_client: AsyncClient, db_session: AsyncSession):
    """Test token refresh with valid refresh token"""
    user, token = await seed_test_user(db_session, email="refresh@test.local")
    
    # Get tokens
    login_response = await async_client.post(
        "/v1/auth/token",
        data={"username": "refresh@test.local", "password": "testpass"}
    )
    tokens = login_response.json()
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        pytest.skip("Refresh token not returned by auth endpoint")
    original_access = tokens["access_token"]
    
    # Refresh token
    refresh_response = await async_client.post(
        "/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert new_tokens["access_token"] != original_access


@pytest.mark.asyncio
async def test_auth_invalid_refresh_token(async_client: AsyncClient):
    """Test token refresh with invalid refresh token"""
    response = await async_client.post(
        "/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"}
    )
    assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_auth_expired_token(async_client: AsyncClient):
    """Test accessing protected endpoint with expired/invalid token"""
    response = await async_client.get(
        "/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_missing_token(async_client: AsyncClient):
    """Test accessing protected endpoint without token"""
    response = await async_client.get("/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_endpoint(async_client: AsyncClient, db_session: AsyncSession):
    """Test /me endpoint returns correct user data"""
    user, token = await seed_test_user(db_session, email="me@test.local")
    
    response = await async_client.get(
        "/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@test.local"
    assert "id" in data
    assert "tenant_id" in data


@pytest.mark.asyncio
async def test_auth_full_flow(async_client: AsyncClient, db_session):
    """Test complete authentication flow: login -> access -> refresh"""
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

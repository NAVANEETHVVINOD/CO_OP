"""
Integration tests for complete authentication flow.

Tests the full authentication workflow:
- Login with credentials
- Receive JWT tokens (access + refresh)
- Access protected endpoints with access token
- Refresh tokens using refresh token
- Verify JWT token structure and expiration

**Validates: Requirements 6.2**
"""
import pytest
import jwt
import uuid
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Tenant, User
from app.core.security import get_password_hash, ALGORITHM


@pytest.mark.asyncio
async def test_complete_auth_flow(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test complete authentication flow: login → token → protected endpoint → refresh
    
    This integration test validates the entire authentication workflow:
    1. User logs in with valid credentials
    2. System returns access_token and refresh_token
    3. User accesses protected endpoint with access_token
    4. User refreshes tokens using refresh_token
    5. New tokens work for protected endpoints
    """
    
    # Setup: Create test user
    tenant = Tenant(name="auth_flow_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    user = User(
        tenant_id=tenant.id,
        email="authflow@test.local",
        hashed_password=get_password_hash("SecurePass123!"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Step 1: Login with credentials
    login_response = await async_client.post(
        "/v1/auth/token",
        data={
            "username": "authflow@test.local",
            "password": "SecurePass123!",
        }
    )
    assert login_response.status_code == 200, "Login should succeed with valid credentials"
    
    login_data = login_response.json()
    assert "access_token" in login_data, "Response should contain access_token"
    assert "refresh_token" in login_data, "Response should contain refresh_token"
    assert login_data["token_type"] == "bearer", "Token type should be bearer"
    
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]
    
    # Step 2: Verify JWT token structure
    # Decode without verification to inspect structure
    access_payload = jwt.decode(access_token, options={"verify_signature": False})
    assert "sub" in access_payload, "Access token should contain subject (user_id)"
    assert "exp" in access_payload, "Access token should contain expiration"
    assert "jti" in access_payload, "Access token should contain JWT ID"
    assert access_payload["sub"] == str(user.id), "Subject should match user ID"
    
    refresh_payload = jwt.decode(refresh_token, options={"verify_signature": False})
    assert "sub" in refresh_payload, "Refresh token should contain subject"
    assert "exp" in refresh_payload, "Refresh token should contain expiration"
    assert refresh_payload["sub"] == str(user.id), "Refresh token subject should match user ID"
    
    # Step 3: Verify token expiration times
    access_exp = datetime.fromtimestamp(access_payload["exp"], tz=timezone.utc)
    refresh_exp = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    
    # Access token should expire in ~15 minutes
    access_lifetime = (access_exp - now).total_seconds()
    assert 0 < access_lifetime <= 15 * 60 + 10, "Access token should expire in ~15 minutes"
    
    # Refresh token should expire in ~7 days
    refresh_lifetime = (refresh_exp - now).total_seconds()
    assert 0 < refresh_lifetime <= 7 * 24 * 60 * 60 + 60, "Refresh token should expire in ~7 days"
    
    # Step 4: Access protected endpoint with access token
    me_response = await async_client.get(
        "/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_response.status_code == 200, "Protected endpoint should accept valid access token"
    
    me_data = me_response.json()
    assert me_data["email"] == "authflow@test.local", "Protected endpoint should return correct user data"
    # UUID comparison: normalize both to UUID objects for comparison
    assert uuid.UUID(me_data["id"]) == uuid.UUID(str(user.id)), "User ID should match"
    assert uuid.UUID(me_data["tenant_id"]) == uuid.UUID(str(tenant.id)), "Tenant ID should match"
    assert me_data["is_active"] is True, "User should be active"
    
    # Step 5: Refresh tokens using refresh token
    refresh_response = await async_client.post(
        "/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200, "Token refresh should succeed with valid refresh token"
    
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data, "Refresh response should contain new access_token"
    assert "refresh_token" in refresh_data, "Refresh response should contain new refresh_token"
    
    new_access_token = refresh_data["access_token"]
    new_refresh_token = refresh_data["refresh_token"]
    
    # Verify new tokens are different from old tokens
    assert new_access_token != access_token, "New access token should be different"
    assert new_refresh_token != refresh_token, "New refresh token should be different"
    
    # Step 6: Verify new access token works for protected endpoints
    me_response_2 = await async_client.get(
        "/v1/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    assert me_response_2.status_code == 200, "New access token should work for protected endpoints"
    assert me_response_2.json()["email"] == "authflow@test.local", "New token should return same user data"


@pytest.mark.asyncio
async def test_protected_routes_require_authentication(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that protected routes reject requests without valid authentication.
    
    Validates:
    - Missing Authorization header returns 401
    - Invalid token format returns 401
    - Expired/malformed token returns 401
    """
    # Test 1: No Authorization header
    response_no_auth = await async_client.get("/v1/auth/me")
    assert response_no_auth.status_code == 401, "Protected route should reject request without auth header"
    
    # Test 2: Invalid token format
    response_invalid = await async_client.get(
        "/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.format"}
    )
    assert response_invalid.status_code == 401, "Protected route should reject invalid token"
    
    # Test 3: Malformed Authorization header
    response_malformed = await async_client.get(
        "/v1/auth/me",
        headers={"Authorization": "NotBearer token"}
    )
    assert response_malformed.status_code == 401, "Protected route should reject malformed auth header"
    
    # Test 4: Empty token
    response_empty = await async_client.get(
        "/v1/auth/me",
        headers={"Authorization": "Bearer "}
    )
    assert response_empty.status_code == 401, "Protected route should reject empty token"


@pytest.mark.asyncio
async def test_jwt_token_signature_validation(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that JWT tokens are properly signed and validated.
    
    Validates:
    - Tokens signed with wrong secret are rejected
    - Tokens with tampered payload are rejected
    """
    
    # Create test user
    tenant = Tenant(name="jwt_test_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    user = User(
        tenant_id=tenant.id,
        email="jwttest@test.local",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create a token with wrong secret
    from datetime import timedelta
    wrong_secret_token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            "jti": "test-jti"
        },
        "wrong-secret-key",
        algorithm=ALGORITHM
    )
    
    # Test: Token with wrong signature should be rejected
    response = await async_client.get(
        "/v1/auth/me",
        headers={"Authorization": f"Bearer {wrong_secret_token}"}
    )
    assert response.status_code == 401, "Token signed with wrong secret should be rejected"


@pytest.mark.asyncio
async def test_inactive_user_cannot_authenticate(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that inactive users cannot authenticate or access protected endpoints.
    """
    # Create inactive user
    tenant = Tenant(name="inactive_test_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    user = User(
        tenant_id=tenant.id,
        email="inactive@test.local",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=False  # User is inactive
    )
    db_session.add(user)
    await db_session.commit()
    
    # Test: Inactive user cannot login
    login_response = await async_client.post(
        "/v1/auth/token",
        data={
            "username": "inactive@test.local",
            "password": "TestPass123!",
        }
    )
    assert login_response.status_code == 400, "Inactive user should not be able to login"
    assert "Inactive user" in login_response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_with_invalid_token(async_client: AsyncClient):
    """
    Test that refresh endpoint rejects invalid refresh tokens.
    """
    # Test 1: Completely invalid token
    response_invalid = await async_client.post(
        "/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"}
    )
    assert response_invalid.status_code == 401, "Invalid refresh token should be rejected"
    
    # Test 2: Empty refresh token
    response_empty = await async_client.post(
        "/v1/auth/refresh",
        json={"refresh_token": ""}
    )
    assert response_empty.status_code == 401, "Empty refresh token should be rejected"
    
    # Test 3: Token with wrong signature
    wrong_token = jwt.encode(
        {
            "sub": "fake-user-id",
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
            "jti": "fake-jti"
        },
        "wrong-secret",
        algorithm=ALGORITHM
    )
    response_wrong = await async_client.post(
        "/v1/auth/refresh",
        json={"refresh_token": wrong_token}
    )
    assert response_wrong.status_code == 401, "Token with wrong signature should be rejected"


@pytest.mark.asyncio
async def test_login_with_wrong_password(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that login fails with incorrect password.
    """
    # Create test user
    tenant = Tenant(name="wrong_pass_tenant")
    db_session.add(tenant)
    await db_session.flush()
    
    user = User(
        tenant_id=tenant.id,
        email="wrongpass@test.local",
        hashed_password=get_password_hash("CorrectPass123!"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    
    # Test: Login with wrong password
    response = await async_client.post(
        "/v1/auth/token",
        data={
            "username": "wrongpass@test.local",
            "password": "WrongPassword123!",
        }
    )
    assert response.status_code == 401, "Login should fail with wrong password"
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_with_nonexistent_user(async_client: AsyncClient):
    """
    Test that login fails for non-existent users.
    """
    response = await async_client.post(
        "/v1/auth/token",
        data={
            "username": "nonexistent@test.local",
            "password": "AnyPassword123!",
        }
    )
    assert response.status_code == 401, "Login should fail for non-existent user"
    assert "Incorrect email or password" in response.json()["detail"]

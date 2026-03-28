import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_health_check(async_client):
    """Test basic health check endpoint"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # Accept both "ok" and "degraded" status (degraded when external services are down)
    assert data["status"] in ["ok", "degraded"]
    assert "services" in data
    assert "postgres" in data["services"]
    assert "redis" in data["services"]
    assert "qdrant" in data["services"]


@pytest.mark.asyncio
async def test_health_check_structure(async_client):
    """Test health check response structure"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    # Check top-level fields
    assert "status" in data
    assert "services" in data
    assert "timestamp" in data
    assert "version" in data
    
    # Check service structure
    for service_name, service_data in data["services"].items():
        assert "status" in service_data
        assert "healthy" in service_data
        assert "latency_ms" in service_data
        assert isinstance(service_data["latency_ms"], (int, float))


@pytest.mark.asyncio
async def test_health_check_postgres_failure(async_client):
    """Test health check when PostgreSQL is down"""
    with patch("app.routers.health._check_postgres", return_value={"status": "down", "healthy": False, "latency_ms": 0, "error": "Connection failed"}):
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["services"]["postgres"]["healthy"] is False


@pytest.mark.asyncio
async def test_health_check_redis_failure(async_client):
    """Test health check when Redis is down"""
    with patch("app.routers.health._check_redis", return_value={"status": "down", "healthy": False, "latency_ms": 0, "error": "Connection failed"}):
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["services"]["redis"]["healthy"] is False


@pytest.mark.asyncio
async def test_health_check_qdrant_failure(async_client):
    """Test health check when Qdrant is down"""
    with patch("app.routers.health._check_qdrant", return_value={"status": "down", "healthy": False, "latency_ms": 0, "error": "Connection failed"}):
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["services"]["qdrant"]["healthy"] is False


@pytest.mark.asyncio
async def test_health_check_multiple_failures(async_client):
    """Test health check when multiple services are down"""
    with patch("app.routers.health._check_postgres", return_value={"status": "down", "healthy": False, "latency_ms": 0}):
        with patch("app.routers.health._check_redis", return_value={"status": "down", "healthy": False, "latency_ms": 0}):
            response = await async_client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["services"]["postgres"]["healthy"] is False
            assert data["services"]["redis"]["healthy"] is False


@pytest.mark.asyncio
async def test_ready_endpoint(async_client):
    """Test ready endpoint"""
    response = await async_client.get("/ready")
    # Ready endpoint returns 200 if healthy, 503 if degraded
    assert response.status_code in [200, 503]


@pytest.mark.asyncio
async def test_ready_endpoint_degraded(async_client):
    """Test ready endpoint when services are degraded"""
    with patch("app.routers.health._check_postgres", return_value={"status": "down", "healthy": False, "latency_ms": 0}):
        response = await async_client.get("/ready")
        assert response.status_code == 503


@pytest.mark.asyncio
async def test_health_latency_measurement(async_client):
    """Test that health check measures service latency"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    # All services should have latency measurements
    for service_name, service_data in data["services"].items():
        assert "latency_ms" in service_data
        assert service_data["latency_ms"] >= 0

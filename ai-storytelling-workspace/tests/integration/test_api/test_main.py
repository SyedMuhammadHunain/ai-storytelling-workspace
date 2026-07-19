"""Integration tests for FastAPI main application."""

import pytest
from httpx import AsyncClient, ASGITransport

from storytelling_workspace.api.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns API information."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI Storytelling Workspace API"
        assert data["version"] == "2.0.0"
        assert data["status"] == "running"
        assert "docs" in data
        assert "health" in data


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-storytelling-workspace-api"
        assert data["version"] == "2.0.0"


@pytest.mark.asyncio
async def test_cors_headers():
    """Test CORS headers are present in responses."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_process_time_header():
    """Test X-Process-Time header is added by middleware."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        # Process time header should be present
        assert "x-process-time" in response.headers
        # Should be in format like "1.23ms"
        assert "ms" in response.headers["x-process-time"]


@pytest.mark.asyncio
async def test_api_docs_accessible():
    """Test API documentation is accessible."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/docs")
        
        assert response.status_code == 200
        # Should return HTML for Swagger UI
        assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_openapi_schema():
    """Test OpenAPI schema is accessible."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "AI Storytelling Workspace API"
        assert schema["info"]["version"] == "2.0.0"


@pytest.mark.asyncio
async def test_404_not_found():
    """Test 404 error for non-existent endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/nonexistent")
        
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_gzip_compression():
    """Test GZIP compression is enabled for large responses."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Request with Accept-Encoding header
        response = await client.get(
            "/api/openapi.json",
            headers={"Accept-Encoding": "gzip"}
        )
        
        assert response.status_code == 200
        # For large responses, content-encoding should be gzip
        # (OpenAPI schema is typically > 1KB)
        if len(response.content) > 1000:
            assert "content-encoding" in response.headers

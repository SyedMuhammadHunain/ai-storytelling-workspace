"""Integration tests for project management endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from storytelling_workspace.api.main import app
from storytelling_workspace.api.dependencies import get_db_session
from storytelling_workspace.db.base import Base


@pytest_asyncio.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    yield async_session_maker
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db):
    """Create test client with mocked database."""
    async def override_get_db():
        async with test_db() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    """Test creating a new project."""
    project_data = {
        "name": "Test Novel",
        "description": "A test novel",
        "genre": "Fantasy",
        "target_length": 80000
    }
    
    response = await client.post("/api/projects/", json=project_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Novel"
    assert data["description"] == "A test novel"
    assert data["genre"] == "Fantasy"
    assert data["target_length"] == 80000
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_project_minimal(client: AsyncClient):
    """Test creating project with minimal data."""
    project_data = {
        "name": "Minimal Novel"
    }
    
    response = await client.post("/api/projects/", json=project_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minimal Novel"
    assert data["description"] is None
    assert data["genre"] is None
    assert data["target_length"] == 80000  # Default value


@pytest.mark.asyncio
async def test_create_project_invalid_name(client: AsyncClient):
    """Test creating project with invalid name."""
    project_data = {
        "name": ""  # Empty name
    }
    
    response = await client.post("/api/projects/", json=project_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_projects_empty(client: AsyncClient):
    """Test listing projects when none exist."""
    response = await client.get("/api/projects/")
    
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_list_projects_with_pagination(client: AsyncClient):
    """Test listing projects with pagination."""
    response = await client.get("/api/projects/?page=1&page_size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient):
    """Test getting non-existent project."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/projects/{fake_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_update_project_not_found(client: AsyncClient):
    """Test updating non-existent project."""
    fake_id = str(uuid4())
    update_data = {
        "name": "Updated Name"
    }
    
    response = await client.put(f"/api/projects/{fake_id}", json=update_data)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_not_found(client: AsyncClient):
    """Test deleting non-existent project."""
    fake_id = str(uuid4())
    response = await client.delete(f"/api/projects/{fake_id}")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_stats_not_found(client: AsyncClient):
    """Test getting stats for non-existent project."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/projects/{fake_id}/stats")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_and_get_project(client: AsyncClient):
    """Test creating and then retrieving a project."""
    # Create project
    project_data = {
        "name": "Test Novel",
        "genre": "Sci-Fi"
    }
    create_response = await client.post("/api/projects/", json=project_data)
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]
    
    # Get project
    get_response = await client.get(f"/api/projects/{project_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == project_id
    assert data["name"] == "Test Novel"
    assert data["genre"] == "Sci-Fi"


@pytest.mark.asyncio
async def test_create_and_update_project(client: AsyncClient):
    """Test creating and then updating a project."""
    # Create project
    project_data = {
        "name": "Original Name"
    }
    create_response = await client.post("/api/projects/", json=project_data)
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]
    
    # Update project
    update_data = {
        "name": "Updated Name",
        "status": "in_progress"
    }
    update_response = await client.put(
        f"/api/projects/{project_id}",
        json=update_data
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "in_progress"


@pytest.mark.asyncio
async def test_create_and_delete_project(client: AsyncClient):
    """Test creating and then deleting a project."""
    # Create project
    project_data = {
        "name": "To Be Deleted"
    }
    create_response = await client.post("/api/projects/", json=project_data)
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]
    
    # Delete project
    delete_response = await client.delete(f"/api/projects/{project_id}")
    assert delete_response.status_code == 204
    
    # Verify project is deleted (soft delete)
    get_response = await client.get(f"/api/projects/{project_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_and_get_stats(client: AsyncClient):
    """Test creating project and getting its stats."""
    # Create project
    project_data = {
        "name": "Stats Test"
    }
    create_response = await client.post("/api/projects/", json=project_data)
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]
    
    # Get stats
    stats_response = await client.get(f"/api/projects/{project_id}/stats")
    assert stats_response.status_code == 200
    data = stats_response.json()
    assert data["project_id"] == project_id
    assert data["status"] == "draft"
    assert "word_count" in data
    assert "chapter_count" in data
    assert "image_count" in data

"""Integration tests for workflow execution endpoints."""

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


@pytest_asyncio.fixture
async def project_id(client: AsyncClient):
    """Create a test project and return its ID."""
    project_data = {
        "name": "Test Workflow Project",
        "genre": "Fantasy"
    }
    response = await client.post("/api/projects/", json=project_data)
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_start_workflow(client: AsyncClient, project_id: str):
    """Test starting a workflow."""
    response = await client.post(
        f"/api/workflow/{project_id}/start",
        json={}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project_id
    assert data["status"] == "running"
    assert data["current_phase"] == "setup"
    assert data["progress_percentage"] == 0.0
    assert data["completed_steps"] == 0
    assert data["total_steps"] == 15
    assert "id" in data
    assert "started_at" in data


@pytest.mark.asyncio
async def test_start_workflow_project_not_found(client: AsyncClient):
    """Test starting workflow for non-existent project."""
    fake_id = str(uuid4())
    response = await client.post(
        f"/api/workflow/{fake_id}/start",
        json={}
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_start_workflow_already_running(client: AsyncClient, project_id: str):
    """Test starting workflow when one is already running."""
    # Start first workflow
    response1 = await client.post(
        f"/api/workflow/{project_id}/start",
        json={}
    )
    assert response1.status_code == 201
    
    # Try to start second workflow
    response2 = await client.post(
        f"/api/workflow/{project_id}/start",
        json={}
    )
    assert response2.status_code == 409  # Conflict


@pytest.mark.asyncio
async def test_get_workflow_status(client: AsyncClient, project_id: str):
    """Test getting workflow status."""
    # Start workflow
    start_response = await client.post(
        f"/api/workflow/{project_id}/start",
        json={}
    )
    assert start_response.status_code == 201
    
    # Get status
    status_response = await client.get(f"/api/workflow/{project_id}/status")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["project_id"] == project_id
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_get_workflow_status_not_found(client: AsyncClient, project_id: str):
    """Test getting status when no workflow exists."""
    response = await client.get(f"/api/workflow/{project_id}/status")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pause_workflow(client: AsyncClient, project_id: str):
    """Test pausing a running workflow."""
    # Start workflow
    start_response = await client.post(
        f"/api/workflow/{project_id}/start",
        json={}
    )
    assert start_response.status_code == 201
    
    # Pause workflow
    pause_response = await client.post(
        f"/api/workflow/{project_id}/pause",
        json={"reason": "User requested pause"}
    )
    assert pause_response.status_code == 200
    data = pause_response.json()
    assert data["status"] == "paused"
    assert "paused_at" in data


@pytest.mark.asyncio
async def test_pause_workflow_not_running(client: AsyncClient, project_id: str):
    """Test pausing when no workflow is running."""
    response = await client.post(
        f"/api/workflow/{project_id}/pause",
        json={}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_resume_workflow(client: AsyncClient, project_id: str):
    """Test resuming a paused workflow."""
    # Start workflow
    await client.post(f"/api/workflow/{project_id}/start", json={})
    
    # Pause workflow
    await client.post(f"/api/workflow/{project_id}/pause", json={})
    
    # Resume workflow
    resume_response = await client.post(
        f"/api/workflow/{project_id}/resume",
        json={"notes": "Resuming after review"}
    )
    assert resume_response.status_code == 200
    data = resume_response.json()
    assert data["status"] == "running"
    assert "resumed_at" in data


@pytest.mark.asyncio
async def test_resume_workflow_not_paused(client: AsyncClient, project_id: str):
    """Test resuming when no paused workflow exists."""
    response = await client.post(
        f"/api/workflow/{project_id}/resume",
        json={}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cancel_workflow(client: AsyncClient, project_id: str):
    """Test cancelling a running workflow."""
    # Start workflow
    await client.post(f"/api/workflow/{project_id}/start", json={})
    
    # Cancel workflow
    cancel_response = await client.post(f"/api/workflow/{project_id}/cancel")
    assert cancel_response.status_code == 200
    data = cancel_response.json()
    assert data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_workflow_not_running(client: AsyncClient, project_id: str):
    """Test cancelling when no workflow is running."""
    response = await client.post(f"/api/workflow/{project_id}/cancel")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_workflow_lifecycle(client: AsyncClient, project_id: str):
    """Test complete workflow lifecycle: start -> pause -> resume -> cancel."""
    # Start
    start_response = await client.post(
        f"/api/workflow/{project_id}/start",
        json={}
    )
    assert start_response.status_code == 201
    assert start_response.json()["status"] == "running"
    
    # Pause
    pause_response = await client.post(
        f"/api/workflow/{project_id}/pause",
        json={}
    )
    assert pause_response.status_code == 200
    assert pause_response.json()["status"] == "paused"
    
    # Resume
    resume_response = await client.post(
        f"/api/workflow/{project_id}/resume",
        json={}
    )
    assert resume_response.status_code == 200
    assert resume_response.json()["status"] == "running"
    
    # Cancel
    cancel_response = await client.post(f"/api/workflow/{project_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"
    
    # Verify final status
    status_response = await client.get(f"/api/workflow/{project_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "cancelled"

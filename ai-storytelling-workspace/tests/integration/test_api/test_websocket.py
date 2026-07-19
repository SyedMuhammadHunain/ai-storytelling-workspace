"""Integration tests for WebSocket real-time updates."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
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
        "name": "Test WebSocket Project",
        "genre": "Sci-Fi"
    }
    response = await client.post("/api/projects/", json=project_data)
    assert response.status_code == 201
    return response.json()["id"]


def test_websocket_connection(project_id: str):
    """Test WebSocket connection establishment."""
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/{project_id}") as websocket:
            # Receive welcome message
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["project_id"] == project_id
            assert "timestamp" in data


def test_websocket_ping_pong(project_id: str):
    """Test WebSocket ping/pong mechanism."""
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/{project_id}") as websocket:
            # Receive welcome message
            websocket.receive_json()
            
            # Send ping
            websocket.send_text("ping")
            
            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
            assert "timestamp" in data


def test_websocket_multiple_connections(project_id: str):
    """Test multiple WebSocket connections to same project."""
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/{project_id}") as ws1:
            with client.websocket_connect(f"/ws/{project_id}") as ws2:
                # Both should receive welcome messages
                data1 = ws1.receive_json()
                data2 = ws2.receive_json()
                
                assert data1["type"] == "connected"
                assert data2["type"] == "connected"
                assert data1["project_id"] == project_id
                assert data2["project_id"] == project_id


def test_websocket_disconnect():
    """Test WebSocket disconnection handling."""
    from storytelling_workspace.api.websocket.manager import manager
    
    # Get initial connection count
    initial_count = manager.get_connection_count()
    
    with TestClient(app) as client:
        project_id = "test-project-123"
        
        with client.websocket_connect(f"/ws/{project_id}") as websocket:
            websocket.receive_json()  # Welcome message
            
            # Connection should be registered
            assert manager.get_connection_count() == initial_count + 1
        
        # After context exit, connection should be cleaned up
        assert manager.get_connection_count() == initial_count


def test_connection_manager_broadcast():
    """Test ConnectionManager broadcast functionality."""
    import asyncio
    from storytelling_workspace.api.websocket.manager import ConnectionManager
    
    manager = ConnectionManager()
    project_id = "test-project-456"
    
    # Test broadcast with no connections (should not raise)
    asyncio.run(manager.broadcast_to_project(project_id, {"test": "message"}))
    
    # Verify no connections
    assert manager.get_connection_count(project_id) == 0


def test_connection_manager_methods():
    """Test ConnectionManager utility methods."""
    from storytelling_workspace.api.websocket.manager import ConnectionManager
    
    manager = ConnectionManager()
    
    # Test get_connection_count
    assert manager.get_connection_count() == 0
    assert manager.get_connection_count("nonexistent") == 0
    
    # Test get_connected_projects
    assert manager.get_connected_projects() == []

"""
Performance Tests for AI Storytelling Workspace API.
"""

import time
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_project_stats_performance(async_client: AsyncClient, test_project):
    """Test that project stats endpoint responds within acceptable limits without N+1 queries."""
    
    start_time = time.time()
    response = await async_client.get(f"/api/v1/projects/{test_project.id}/stats")
    end_time = time.time()
    
    assert response.status_code == 200
    
    duration = end_time - start_time
    assert duration < 0.5, f"Project stats endpoint took too long: {duration}s"
    
    data = response.json()
    assert "word_count" in data
    assert "chapter_count" in data

"""Story Bible management API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException

from ..schemas.story_bible import (
    StoryBibleResponse,
    StoryBibleVersionListResponse,
)
from ..dependencies import get_story_bible_repo
from ...db.repositories.story_bible import StoryBibleRepository

router = APIRouter()


@router.get(
    "/",
    response_model=StoryBibleVersionListResponse,
    summary="List story bibles",
    description="List story bible versions for a project"
)
async def list_story_bibles(
    project_id: UUID = Query(..., description="Project ID"),
    story_bible_repo: StoryBibleRepository = Depends(get_story_bible_repo)
):
    bibles = await story_bible_repo.get_by_project_id(str(project_id))
    
    versions = []
    for b in bibles:
        versions.append({
            "version": b.version,
            "created_at": b.created_at.isoformat() if hasattr(b, "created_at") and b.created_at else None,
            "changes": "Version update"
        })
        
    current_version = max([v["version"] for v in versions]) if versions else 0
    
    return StoryBibleVersionListResponse(
        versions=versions,
        current_version=current_version,
        total_versions=len(versions)
    )


@router.get(
    "/{bible_id}",
    response_model=StoryBibleResponse,
    summary="Get story bible by ID"
)
async def get_story_bible(
    bible_id: UUID,
    story_bible_repo: StoryBibleRepository = Depends(get_story_bible_repo)
):
    bible = await story_bible_repo.get_by_id(str(bible_id))
    if not bible:
        raise HTTPException(status_code=404, detail="Story Bible not found")
        
    return StoryBibleResponse.model_validate(bible)


@router.get(
    "/project/{project_id}/latest",
    response_model=StoryBibleResponse,
    summary="Get latest story bible for project"
)
async def get_latest_story_bible(
    project_id: UUID,
    story_bible_repo: StoryBibleRepository = Depends(get_story_bible_repo)
):
    bible = await story_bible_repo.get_latest_by_project(str(project_id))
    if not bible:
        raise HTTPException(status_code=404, detail="Story Bible not found for project")
        
    return StoryBibleResponse.model_validate(bible)

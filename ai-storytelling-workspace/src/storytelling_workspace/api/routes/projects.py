"""Project management API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from ..schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatsResponse,
)
from ..dependencies import get_project_repo, get_story_bible_repo
from ..exceptions import ProjectNotFoundException
from ...db.repositories import ProjectRepository, StoryBibleRepository

router = APIRouter()


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a new storytelling project with optional metadata"
)
async def create_project(
    project: ProjectCreate,
    project_repo: ProjectRepository = Depends(get_project_repo),
    story_bible_repo: StoryBibleRepository = Depends(get_story_bible_repo)
):
    """
    Create a new project and initialize its Story Bible.
    
    Args:
        project: Project creation data
        project_repo: Project repository
        story_bible_repo: Story Bible repository
        
    Returns:
        Created project
    """
    # Create project
    project_data = project.model_dump()
    db_project = await project_repo.create(**project_data)
    
    # Initialize Story Bible for the project
    bible_data = {
        "project_id": str(db_project.id),
        "version": 1,
        "brief": {},
        "concept": {},
        "world_rules": {},
        "characters": {},
        "locations": {},
        "timeline": {},
        "plot_threads": {},
        "terminology": {},
        "style_guide": {},
        "metadata": {}
    }
    await story_bible_repo.create(**bible_data)
    
    return ProjectResponse.model_validate(db_project)


@router.get(
    "/",
    response_model=ProjectListResponse,
    summary="List all projects",
    description="Get paginated list of projects with optional filtering"
)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    project_repo: ProjectRepository = Depends(get_project_repo)
):
    """
    List all projects with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        status: Optional status filter
        genre: Optional genre filter
        project_repo: Project repository
        
    Returns:
        Paginated list of projects
    """
    # Build filters
    filters = {}
    if status:
        filters["status"] = status
    if genre:
        filters["genre"] = genre
    
    # Get projects
    skip = (page - 1) * page_size
    projects = await project_repo.list(
        skip=skip,
        limit=page_size,
        filters=filters
    )
    
    # Get total count
    total = await project_repo.count(filters=filters)
    
    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
    description="Retrieve a specific project by its UUID"
)
async def get_project(
    project_id: UUID,
    project_repo: ProjectRepository = Depends(get_project_repo)
):
    """
    Get a project by ID.
    
    Args:
        project_id: Project UUID
        project_repo: Project repository
        
    Returns:
        Project details
        
    Raises:
        ProjectNotFoundException: If project not found
    """
    project = await project_repo.get_by_id(str(project_id))
    if not project:
        raise ProjectNotFoundException(str(project_id))
    
    return ProjectResponse.model_validate(project)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update an existing project's metadata"
)
async def update_project(
    project_id: UUID,
    updates: ProjectUpdate,
    project_repo: ProjectRepository = Depends(get_project_repo)
):
    """
    Update a project.
    
    Args:
        project_id: Project UUID
        updates: Fields to update
        project_repo: Project repository
        
    Returns:
        Updated project
        
    Raises:
        ProjectNotFoundException: If project not found
    """
    # Check project exists
    project = await project_repo.get_by_id(str(project_id))
    if not project:
        raise ProjectNotFoundException(str(project_id))
    
    # Update project
    update_data = updates.model_dump(exclude_unset=True)
    if update_data:  # Only update if there are changes
        updated_project = await project_repo.update(str(project_id), **update_data)
        return ProjectResponse.model_validate(updated_project)
    
    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Soft delete a project (marks as deleted but preserves data)"
)
async def delete_project(
    project_id: UUID,
    project_repo: ProjectRepository = Depends(get_project_repo)
):
    """
    Delete a project (soft delete).
    
    Args:
        project_id: Project UUID
        project_repo: Project repository
        
    Raises:
        ProjectNotFoundException: If project not found
    """
    # Check project exists
    project = await project_repo.get_by_id(str(project_id))
    if not project:
        raise ProjectNotFoundException(str(project_id))
    
    # Soft delete
    await project_repo.delete(str(project_id))
    
    return None


@router.get(
    "/{project_id}/stats",
    response_model=ProjectStatsResponse,
    summary="Get project statistics",
    description="Get detailed statistics for a project"
)
async def get_project_stats(
    project_id: UUID,
    project_repo: ProjectRepository = Depends(get_project_repo),
    story_bible_repo: StoryBibleRepository = Depends(get_story_bible_repo)
):
    """
    Get project statistics.
    
    Args:
        project_id: Project UUID
        project_repo: Project repository
        story_bible_repo: Story Bible repository
        
    Returns:
        Project statistics
        
    Raises:
        ProjectNotFoundException: If project not found
    """
    # Check project exists
    project = await project_repo.get_by_id(str(project_id))
    if not project:
        raise ProjectNotFoundException(str(project_id))
    
    # Get Story Bible version
    bible = await story_bible_repo.get_latest_by_project(str(project_id))
    bible_version = bible.version if bible else 0
    
    # TODO: Calculate actual stats from related tables
    # For now, return placeholder values
    return ProjectStatsResponse(
        project_id=project_id,
        status=project.status,
        word_count=0,  # TODO: Calculate from chapters
        chapter_count=0,  # TODO: Count chapters
        image_count=0,  # TODO: Count images
        checkpoint_count=0,  # TODO: Count checkpoints
        bible_version=bible_version
    )

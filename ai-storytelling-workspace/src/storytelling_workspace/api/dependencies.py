"""Dependency injection for FastAPI routes."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..db.repositories import (
    ProjectRepository,
    StoryBibleRepository,
    CheckpointRepository,
    ImageRepository,
    WorkflowStateRepository,
)


# Database session dependency
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            ...
    
    Yields:
        AsyncSession instance
    """
    async for session in get_db():
        yield session


# Repository dependencies
async def get_project_repo(
    db: AsyncSession = Depends(get_db_session)
) -> ProjectRepository:
    """
    Get project repository instance.
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        ProjectRepository instance
    """
    return ProjectRepository(db)


async def get_story_bible_repo(
    db: AsyncSession = Depends(get_db_session)
) -> StoryBibleRepository:
    """
    Get story bible repository instance.
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        StoryBibleRepository instance
    """
    return StoryBibleRepository(db)


async def get_checkpoint_repo(
    db: AsyncSession = Depends(get_db_session)
) -> CheckpointRepository:
    """
    Get checkpoint repository instance.
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        CheckpointRepository instance
    """
    return CheckpointRepository(db)


async def get_image_repo(
    db: AsyncSession = Depends(get_db_session)
) -> ImageRepository:
    """
    Get image repository instance.
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        ImageRepository instance
    """
    return ImageRepository(db)


async def get_workflow_repo(
    db: AsyncSession = Depends(get_db_session)
) -> WorkflowStateRepository:
    """
    Get workflow state repository instance.
    
    Args:
        db: Database session from dependency injection
        
    Returns:
        WorkflowStateRepository instance
    """
    return WorkflowStateRepository(db)


# Composite dependencies for services that need multiple repositories
class RepositoryDependencies:
    """Container for multiple repository dependencies."""
    
    def __init__(
        self,
        project_repo: ProjectRepository = Depends(get_project_repo),
        story_bible_repo: StoryBibleRepository = Depends(get_story_bible_repo),
        checkpoint_repo: CheckpointRepository = Depends(get_checkpoint_repo),
        image_repo: ImageRepository = Depends(get_image_repo),
        workflow_repo: WorkflowStateRepository = Depends(get_workflow_repo),
    ):
        """
        Initialize repository dependencies.
        
        Args:
            project_repo: Project repository
            story_bible_repo: Story Bible repository
            checkpoint_repo: Checkpoint repository
            image_repo: Image repository
            workflow_repo: Workflow state repository
        """
        self.project = project_repo
        self.story_bible = story_bible_repo
        self.checkpoint = checkpoint_repo
        self.image = image_repo
        self.workflow = workflow_repo

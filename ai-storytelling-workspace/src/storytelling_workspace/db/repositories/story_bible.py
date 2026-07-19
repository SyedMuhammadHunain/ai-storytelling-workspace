"""
StoryBible repository for CRUD operations on StoryBible model.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from storytelling_workspace.db.models.story_bible import StoryBible
from storytelling_workspace.db.repositories.base import BaseRepository


class StoryBibleRepository(BaseRepository[StoryBible]):
    """Repository for StoryBible model with custom queries."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize StoryBible repository.
        
        Args:
            session: Async database session
        """
        super().__init__(StoryBible, session)
    
    async def get_by_project_id(self, project_id: str | UUID) -> List[StoryBible]:
        """
        Get all story bibles for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of story bibles ordered by version (newest first)
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(StoryBible)
            .where(StoryBible.project_id == project_id_str)
            .order_by(StoryBible.version.desc())
        )
        
        result = await self.session.execute(stmt)
        bibles = result.scalars().all()
        
        self.logger.debug(f"Retrieved {len(bibles)} story bibles for project {project_id_str}")
        return list(bibles)
    
    async def get_latest_by_project(self, project_id: str | UUID) -> Optional[StoryBible]:
        """
        Get the latest version of story bible for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Latest story bible or None if not found
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(StoryBible)
            .where(StoryBible.project_id == project_id_str)
            .order_by(StoryBible.version.desc())
            .limit(1)
        )
        
        result = await self.session.execute(stmt)
        bible = result.scalar_one_or_none()
        
        if bible:
            self.logger.debug(f"Found latest story bible (v{bible.version}) for project {project_id_str}")
        else:
            self.logger.debug(f"No story bible found for project {project_id_str}")
        
        return bible
    
    async def get_by_version(self, project_id: str | UUID, version: int) -> Optional[StoryBible]:
        """
        Get specific version of story bible for a project.
        
        Args:
            project_id: Project ID
            version: Version number
            
        Returns:
            Story bible or None if not found
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(StoryBible)
            .where(StoryBible.project_id == project_id_str)
            .where(StoryBible.version == version)
        )
        
        result = await self.session.execute(stmt)
        bible = result.scalar_one_or_none()
        
        if bible:
            self.logger.debug(f"Found story bible v{version} for project {project_id_str}")
        else:
            self.logger.debug(f"Story bible v{version} not found for project {project_id_str}")
        
        return bible
    
    async def increment_version(self, id: str | UUID) -> Optional[StoryBible]:
        """
        Increment the version number of a story bible.
        
        Args:
            id: Story bible ID
            
        Returns:
            Updated story bible or None if not found
        """
        bible = await self.get_by_id(id)
        if not bible:
            return None
        
        bible.increment_version()
        await self.session.flush()
        await self.session.refresh(bible)
        
        self.logger.info(f"Incremented story bible version to {bible.version}")
        return bible
    
    async def update_section(
        self,
        id: str | UUID,
        section_name: str,
        data: dict
    ) -> Optional[StoryBible]:
        """
        Update a specific section of the story bible.
        
        Args:
            id: Story bible ID
            section_name: Name of section to update
            data: New section data
            
        Returns:
            Updated story bible or None if not found
        """
        bible = await self.get_by_id(id)
        if not bible:
            return None
        
        bible.update_section(section_name, data)
        await self.session.flush()
        await self.session.refresh(bible)
        
        self.logger.info(f"Updated section '{section_name}' in story bible {id}")
        return bible
    
    async def get_with_chapters(self, id: str | UUID) -> Optional[StoryBible]:
        """
        Get story bible with all chapters eagerly loaded.
        
        Args:
            id: Story bible ID
            
        Returns:
            Story bible with chapters or None if not found
        """
        id_str = str(id) if isinstance(id, UUID) else id
        
        stmt = (
            select(StoryBible)
            .where(StoryBible.id == id_str)
            .options(selectinload(StoryBible.chapters))
        )
        
        result = await self.session.execute(stmt)
        bible = result.scalar_one_or_none()
        
        if bible:
            self.logger.debug(f"Loaded story bible {id_str} with {len(bible.chapters)} chapters")
        
        return bible
    
    async def get_with_images(self, id: str | UUID) -> Optional[StoryBible]:
        """
        Get story bible with all images eagerly loaded.
        
        Args:
            id: Story bible ID
            
        Returns:
            Story bible with images or None if not found
        """
        id_str = str(id) if isinstance(id, UUID) else id
        
        stmt = (
            select(StoryBible)
            .where(StoryBible.id == id_str)
            .options(selectinload(StoryBible.images))
        )
        
        result = await self.session.execute(stmt)
        bible = result.scalar_one_or_none()
        
        if bible:
            self.logger.debug(f"Loaded story bible {id_str} with {len(bible.images)} images")
        
        return bible
    
    async def get_complete(self, id: str | UUID) -> Optional[StoryBible]:
        """
        Get story bible with all related data eagerly loaded.
        
        Args:
            id: Story bible ID
            
        Returns:
            Complete story bible or None if not found
        """
        id_str = str(id) if isinstance(id, UUID) else id
        
        stmt = (
            select(StoryBible)
            .where(StoryBible.id == id_str)
            .options(
                selectinload(StoryBible.chapters),
                selectinload(StoryBible.images),
                selectinload(StoryBible.checkpoints),
                selectinload(StoryBible.agent_deltas)
            )
        )
        
        result = await self.session.execute(stmt)
        bible = result.scalar_one_or_none()
        
        if bible:
            self.logger.debug(
                f"Loaded complete story bible {id_str} with "
                f"{len(bible.chapters)} chapters, {len(bible.images)} images, "
                f"{len(bible.checkpoints)} checkpoints, {len(bible.agent_deltas)} deltas"
            )
        
        return bible

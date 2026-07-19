"""
Project repository for CRUD operations on Project model.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from storytelling_workspace.db.models.project import Project, ProjectStatus
from storytelling_workspace.db.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model with custom queries."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize Project repository.
        
        Args:
            session: Async database session
        """
        super().__init__(Project, session)
    
    async def get_by_status(self, status: ProjectStatus) -> List[Project]:
        """
        Get all projects with specific status.
        
        Args:
            status: Project status to filter by
            
        Returns:
            List of projects with the given status
        """
        return await self.filter_by(status=status)
    
    async def get_active_projects(self) -> List[Project]:
        """
        Get all active projects (not archived or deleted).
        
        Returns:
            List of active projects
        """
        stmt = (
            select(Project)
            .where(Project.deleted_at.is_(None))
            .where(Project.status != ProjectStatus.ARCHIVED)
            .order_by(Project.updated_at.desc())
        )
        
        result = await self.session.execute(stmt)
        projects = result.scalars().all()
        
        self.logger.debug(f"Retrieved {len(projects)} active projects")
        return list(projects)
    
    async def get_deleted_projects(self) -> List[Project]:
        """
        Get all soft-deleted projects.
        
        Returns:
            List of deleted projects
        """
        stmt = (
            select(Project)
            .where(Project.deleted_at.is_not(None))
            .order_by(Project.deleted_at.desc())
        )
        
        result = await self.session.execute(stmt)
        projects = result.scalars().all()
        
        self.logger.debug(f"Retrieved {len(projects)} deleted projects")
        return list(projects)
    
    async def soft_delete(self, id: str | UUID) -> bool:
        """
        Soft delete a project.
        
        Args:
            id: Project ID
            
        Returns:
            True if deleted, False if not found
        """
        project = await self.get_by_id(id)
        if not project:
            return False
        
        project.soft_delete()
        await self.session.flush()
        
        self.logger.info(f"Soft deleted project with id={id}")
        return True
    
    async def restore(self, id: str | UUID) -> Optional[Project]:
        """
        Restore a soft-deleted project.
        
        Args:
            id: Project ID
            
        Returns:
            Restored project or None if not found
        """
        project = await self.get_by_id(id)
        if not project:
            return None
        
        project.restore()
        await self.session.flush()
        await self.session.refresh(project)
        
        self.logger.info(f"Restored project with id={id}")
        return project
    
    async def update_status(self, id: str | UUID, status: ProjectStatus) -> Optional[Project]:
        """
        Update project status.
        
        Args:
            id: Project ID
            status: New status
            
        Returns:
            Updated project or None if not found
        """
        return await self.update(id, status=status)
    
    async def search_by_name(self, name_query: str) -> List[Project]:
        """
        Search projects by name (case-insensitive partial match).
        
        Args:
            name_query: Search query
            
        Returns:
            List of matching projects
        """
        stmt = (
            select(Project)
            .where(Project.name.ilike(f"%{name_query}%"))
            .where(Project.deleted_at.is_(None))
            .order_by(Project.name)
        )
        
        result = await self.session.execute(stmt)
        projects = result.scalars().all()
        
        self.logger.debug(f"Found {len(projects)} projects matching '{name_query}'")
        return list(projects)
    
    async def get_by_genre(self, genre: str) -> List[Project]:
        """
        Get projects by genre.
        
        Args:
            genre: Genre to filter by
            
        Returns:
            List of projects with the given genre
        """
        return await self.filter_by(genre=genre)
    
    async def get_recent(self, limit: int = 10) -> List[Project]:
        """
        Get most recently updated projects.
        
        Args:
            limit: Maximum number of projects to return
            
        Returns:
            List of recent projects
        """
        stmt = (
            select(Project)
            .where(Project.deleted_at.is_(None))
            .order_by(Project.updated_at.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        projects = result.scalars().all()
        
        self.logger.debug(f"Retrieved {len(projects)} recent projects")
        return list(projects)

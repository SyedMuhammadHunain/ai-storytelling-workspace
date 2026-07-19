"""
Checkpoint repository for CRUD operations on Checkpoint model.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from storytelling_workspace.db.models.checkpoint import Checkpoint, CheckpointStatus, CheckpointType
from storytelling_workspace.db.repositories.base import BaseRepository


class CheckpointRepository(BaseRepository[Checkpoint]):
    """Repository for Checkpoint model with custom queries."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize Checkpoint repository.
        
        Args:
            session: Async database session
        """
        super().__init__(Checkpoint, session)
    
    async def get_by_project_id(self, project_id: str | UUID) -> List[Checkpoint]:
        """
        Get all checkpoints for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of checkpoints ordered by creation time (newest first)
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Checkpoint)
            .where(Checkpoint.project_id == project_id_str)
            .order_by(Checkpoint.created_at.desc())
        )
        
        result = await self.session.execute(stmt)
        checkpoints = result.scalars().all()
        
        self.logger.debug(f"Retrieved {len(checkpoints)} checkpoints for project {project_id_str}")
        return list(checkpoints)
    
    async def get_pending_checkpoints(self, project_id: str | UUID) -> List[Checkpoint]:
        """
        Get all pending checkpoints for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of pending checkpoints
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Checkpoint)
            .where(Checkpoint.project_id == project_id_str)
            .where(Checkpoint.status == CheckpointStatus.PENDING)
            .order_by(Checkpoint.created_at)
        )
        
        result = await self.session.execute(stmt)
        checkpoints = result.scalars().all()
        
        self.logger.debug(f"Found {len(checkpoints)} pending checkpoints for project {project_id_str}")
        return list(checkpoints)
    
    async def get_by_type(
        self,
        project_id: str | UUID,
        checkpoint_type: CheckpointType
    ) -> List[Checkpoint]:
        """
        Get checkpoints by type for a project.
        
        Args:
            project_id: Project ID
            checkpoint_type: Type of checkpoint
            
        Returns:
            List of checkpoints of the given type
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Checkpoint)
            .where(Checkpoint.project_id == project_id_str)
            .where(Checkpoint.checkpoint_type == checkpoint_type)
            .order_by(Checkpoint.created_at.desc())
        )
        
        result = await self.session.execute(stmt)
        checkpoints = result.scalars().all()
        
        self.logger.debug(
            f"Found {len(checkpoints)} {checkpoint_type.value} checkpoints for project {project_id_str}"
        )
        return list(checkpoints)
    
    async def get_by_status(
        self,
        project_id: str | UUID,
        status: CheckpointStatus
    ) -> List[Checkpoint]:
        """
        Get checkpoints by status for a project.
        
        Args:
            project_id: Project ID
            status: Checkpoint status
            
        Returns:
            List of checkpoints with the given status
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Checkpoint)
            .where(Checkpoint.project_id == project_id_str)
            .where(Checkpoint.status == status)
            .order_by(Checkpoint.created_at.desc())
        )
        
        result = await self.session.execute(stmt)
        checkpoints = result.scalars().all()
        
        self.logger.debug(
            f"Found {len(checkpoints)} {status.value} checkpoints for project {project_id_str}"
        )
        return list(checkpoints)
    
    async def approve(self, id: str | UUID, feedback: Optional[str] = None) -> Optional[Checkpoint]:
        """
        Approve a checkpoint.
        
        Args:
            id: Checkpoint ID
            feedback: Optional user feedback
            
        Returns:
            Updated checkpoint or None if not found
        """
        checkpoint = await self.get_by_id(id)
        if not checkpoint:
            return None
        
        checkpoint.approve(feedback)
        await self.session.flush()
        await self.session.refresh(checkpoint)
        
        self.logger.info(f"Approved checkpoint {id}")
        return checkpoint
    
    async def reject(self, id: str | UUID, reason: str) -> Optional[Checkpoint]:
        """
        Reject a checkpoint.
        
        Args:
            id: Checkpoint ID
            reason: Reason for rejection
            
        Returns:
            Updated checkpoint or None if not found
        """
        checkpoint = await self.get_by_id(id)
        if not checkpoint:
            return None
        
        checkpoint.reject(reason)
        await self.session.flush()
        await self.session.refresh(checkpoint)
        
        self.logger.info(f"Rejected checkpoint {id}: {reason}")
        return checkpoint
    
    async def skip(self, id: str | UUID) -> Optional[Checkpoint]:
        """
        Skip a checkpoint.
        
        Args:
            id: Checkpoint ID
            
        Returns:
            Updated checkpoint or None if not found
        """
        checkpoint = await self.get_by_id(id)
        if not checkpoint:
            return None
        
        checkpoint.skip()
        await self.session.flush()
        await self.session.refresh(checkpoint)
        
        self.logger.info(f"Skipped checkpoint {id}")
        return checkpoint
    
    async def get_latest_by_type(
        self,
        project_id: str | UUID,
        checkpoint_type: CheckpointType
    ) -> Optional[Checkpoint]:
        """
        Get the most recent checkpoint of a specific type.
        
        Args:
            project_id: Project ID
            checkpoint_type: Type of checkpoint
            
        Returns:
            Latest checkpoint or None if not found
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Checkpoint)
            .where(Checkpoint.project_id == project_id_str)
            .where(Checkpoint.checkpoint_type == checkpoint_type)
            .order_by(Checkpoint.created_at.desc())
            .limit(1)
        )
        
        result = await self.session.execute(stmt)
        checkpoint = result.scalar_one_or_none()
        
        if checkpoint:
            self.logger.debug(
                f"Found latest {checkpoint_type.value} checkpoint for project {project_id_str}"
            )
        
        return checkpoint

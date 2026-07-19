"""
WorkflowState repository for CRUD operations on WorkflowState model.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from storytelling_workspace.db.models.workflow_state import WorkflowState, WorkflowStatus
from storytelling_workspace.db.repositories.base import BaseRepository


class WorkflowStateRepository(BaseRepository[WorkflowState]):
    """Repository for WorkflowState model with custom queries."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize WorkflowState repository.
        
        Args:
            session: Async database session
        """
        super().__init__(WorkflowState, session)
    
    async def get_by_project_id(self, project_id: str | UUID) -> Optional[WorkflowState]:
        """
        Get workflow state for a project (should be unique).
        
        Args:
            project_id: Project ID
            
        Returns:
            Workflow state or None if not found
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = select(WorkflowState).where(WorkflowState.project_id == project_id_str)
        result = await self.session.execute(stmt)
        state = result.scalar_one_or_none()
        
        if state:
            self.logger.debug(f"Found workflow state for project {project_id_str}")
        else:
            self.logger.debug(f"No workflow state found for project {project_id_str}")
        
        return state
    
    async def get_by_status(self, status: WorkflowStatus) -> List[WorkflowState]:
        """
        Get all workflow states with specific status.
        
        Args:
            status: Workflow status to filter by
            
        Returns:
            List of workflow states with the given status
        """
        return await self.filter_by(status=status)
    
    async def get_running_workflows(self) -> List[WorkflowState]:
        """
        Get all currently running workflows.
        
        Returns:
            List of running workflow states
        """
        return await self.get_by_status(WorkflowStatus.RUNNING)
    
    async def get_paused_workflows(self) -> List[WorkflowState]:
        """
        Get all paused workflows.
        
        Returns:
            List of paused workflow states
        """
        return await self.get_by_status(WorkflowStatus.PAUSED)
    
    async def start(self, id: str | UUID) -> Optional[WorkflowState]:
        """
        Start a workflow.
        
        Args:
            id: Workflow state ID
            
        Returns:
            Updated workflow state or None if not found
        """
        state = await self.get_by_id(id)
        if not state:
            return None
        
        state.start()
        await self.session.flush()
        await self.session.refresh(state)
        
        self.logger.info(f"Started workflow {id}")
        return state
    
    async def pause(self, id: str | UUID) -> Optional[WorkflowState]:
        """
        Pause a workflow.
        
        Args:
            id: Workflow state ID
            
        Returns:
            Updated workflow state or None if not found
        """
        state = await self.get_by_id(id)
        if not state:
            return None
        
        state.pause()
        await self.session.flush()
        await self.session.refresh(state)
        
        self.logger.info(f"Paused workflow {id}")
        return state
    
    async def resume(self, id: str | UUID) -> Optional[WorkflowState]:
        """
        Resume a paused workflow.
        
        Args:
            id: Workflow state ID
            
        Returns:
            Updated workflow state or None if not found
        """
        state = await self.get_by_id(id)
        if not state:
            return None
        
        state.resume()
        await self.session.flush()
        await self.session.refresh(state)
        
        self.logger.info(f"Resumed workflow {id}")
        return state
    
    async def complete(self, id: str | UUID) -> Optional[WorkflowState]:
        """
        Mark workflow as completed.
        
        Args:
            id: Workflow state ID
            
        Returns:
            Updated workflow state or None if not found
        """
        state = await self.get_by_id(id)
        if not state:
            return None
        
        state.complete()
        await self.session.flush()
        await self.session.refresh(state)
        
        self.logger.info(f"Completed workflow {id}")
        return state
    
    async def fail(self, id: str | UUID, error: str) -> Optional[WorkflowState]:
        """
        Mark workflow as failed.
        
        Args:
            id: Workflow state ID
            error: Error message
            
        Returns:
            Updated workflow state or None if not found
        """
        state = await self.get_by_id(id)
        if not state:
            return None
        
        state.fail(error)
        await self.session.flush()
        await self.session.refresh(state)
        
        self.logger.info(f"Failed workflow {id}: {error}")
        return state
    
    async def update_progress(
        self,
        id: str | UUID,
        current_step: str,
        progress_percentage: int
    ) -> Optional[WorkflowState]:
        """
        Update workflow progress.
        
        Args:
            id: Workflow state ID
            current_step: Current step name
            progress_percentage: Progress percentage (0-100)
            
        Returns:
            Updated workflow state or None if not found
        """
        state = await self.get_by_id(id)
        if not state:
            return None
        
        state.update_progress(current_step, progress_percentage)
        await self.session.flush()
        await self.session.refresh(state)
        
        self.logger.info(f"Updated workflow {id} progress: {current_step} ({progress_percentage}%)")
        return state
    
    async def get_or_create_for_project(self, project_id: str | UUID) -> tuple[WorkflowState, bool]:
        """
        Get existing workflow state or create new one for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Tuple of (workflow_state, created) where created is True if new
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        # Try to find existing
        state = await self.get_by_project_id(project_id_str)
        if state:
            return state, False
        
        # Create new
        state = await self.create(
            project_id=project_id_str,
            status=WorkflowStatus.PENDING,
            current_step="initialization",
            progress_percentage=0
        )
        
        self.logger.info(f"Created new workflow state for project {project_id_str}")
        return state, True
    
    async def get_active_by_project(self, project_id: str | UUID) -> Optional[WorkflowState]:
        """
        Get active (running or paused) workflow for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Active workflow state or None if not found
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(WorkflowState)
            .where(WorkflowState.project_id == project_id_str)
            .where(WorkflowState.status.in_([WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]))
            .order_by(WorkflowState.started_at.desc())
        )
        
        result = await self.session.execute(stmt)
        state = result.scalar_one_or_none()
        
        if state:
            self.logger.debug(f"Found active workflow for project {project_id_str}")
        else:
            self.logger.debug(f"No active workflow found for project {project_id_str}")
        
        return state
    
    async def get_latest_by_project(self, project_id: str | UUID) -> Optional[WorkflowState]:
        """
        Get latest workflow for a project (any status).
        
        Args:
            project_id: Project ID
            
        Returns:
            Latest workflow state or None if not found
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(WorkflowState)
            .where(WorkflowState.project_id == project_id_str)
            .order_by(WorkflowState.started_at.desc())
        )
        
        result = await self.session.execute(stmt)
        state = result.scalar_one_or_none()
        
        if state:
            self.logger.debug(f"Found latest workflow for project {project_id_str}")
        else:
            self.logger.debug(f"No workflow found for project {project_id_str}")
        
        return state
    
    async def get_by_project_and_status(
        self,
        project_id: str | UUID,
        status: str
    ) -> Optional[WorkflowState]:
        """
        Get workflow for a project with specific status.
        
        Args:
            project_id: Project ID
            status: Workflow status
            
        Returns:
            Workflow state or None if not found
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(WorkflowState)
            .where(WorkflowState.project_id == project_id_str)
            .where(WorkflowState.status == status)
            .order_by(WorkflowState.started_at.desc())
        )
        
        result = await self.session.execute(stmt)
        state = result.scalar_one_or_none()
        
        if state:
            self.logger.debug(f"Found workflow with status {status} for project {project_id_str}")
        else:
            self.logger.debug(f"No workflow with status {status} found for project {project_id_str}")
        
        return state

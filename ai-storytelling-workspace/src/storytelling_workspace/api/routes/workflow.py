"""Workflow execution API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status

from ..schemas.workflow import (
    WorkflowStartRequest,
    WorkflowPauseRequest,
    WorkflowResumeRequest,
    WorkflowStatusResponse,
)
from ..dependencies import get_workflow_repo, get_project_repo
from ..exceptions import (
    ProjectNotFoundException,
    WorkflowAlreadyRunningException,
    WorkflowNotFoundException,
    WorkflowNotRunningException,
)
from ...db.repositories import WorkflowStateRepository, ProjectRepository

router = APIRouter()


@router.post(
    "/{project_id}/start",
    response_model=WorkflowStatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start workflow execution",
    description="Start async workflow execution for a project"
)
async def start_workflow(
    project_id: UUID,
    request: WorkflowStartRequest,
    project_repo: ProjectRepository = Depends(get_project_repo),
    workflow_repo: WorkflowStateRepository = Depends(get_workflow_repo)
):
    """
    Start workflow execution for a project.
    
    Args:
        project_id: Project UUID
        request: Workflow start request
        project_repo: Project repository
        workflow_repo: Workflow state repository
        
    Returns:
        Created workflow state
        
    Raises:
        ProjectNotFoundException: If project not found
        WorkflowAlreadyRunningException: If workflow already running
    """
    # Verify project exists
    project = await project_repo.get_by_id(str(project_id))
    if not project:
        raise ProjectNotFoundException(str(project_id))
    
    # Check if workflow already running
    existing = await workflow_repo.get_active_by_project(str(project_id))
    if existing:
        raise WorkflowAlreadyRunningException(str(project_id))
    
    # Create workflow state
    workflow_data = {
        "project_id": str(project_id),
        "status": "running",
        "current_phase": "setup",
        "current_agent": None,
        "progress_percentage": 0.0,
        "completed_steps": 0,
        "total_steps": 15,  # Total number of agents
        "error_message": None
    }
    
    workflow_state = await workflow_repo.create(**workflow_data)
    
    # TODO: Dispatch Celery task for async execution
    # from ...workers.workflow_tasks import start_workflow_task
    # start_workflow_task.delay(str(project_id), str(workflow_state.id))
    
    return WorkflowStatusResponse.model_validate(workflow_state)


@router.post(
    "/{project_id}/pause",
    response_model=WorkflowStatusResponse,
    summary="Pause workflow execution",
    description="Pause a running workflow"
)
async def pause_workflow(
    project_id: UUID,
    request: WorkflowPauseRequest,
    workflow_repo: WorkflowStateRepository = Depends(get_workflow_repo)
):
    """
    Pause a running workflow.
    
    Args:
        project_id: Project UUID
        request: Pause request with optional reason
        workflow_repo: Workflow state repository
        
    Returns:
        Updated workflow state
        
    Raises:
        WorkflowNotRunningException: If no active workflow found
    """
    # Get active workflow
    workflow = await workflow_repo.get_active_by_project(str(project_id))
    if not workflow:
        raise WorkflowNotRunningException(str(project_id))
    
    # Update workflow state
    updated = await workflow_repo.update(
        str(workflow.id),
        status="paused"
    )
    
    # TODO: Signal Celery task to pause
    
    return WorkflowStatusResponse.model_validate(updated)


@router.post(
    "/{project_id}/resume",
    response_model=WorkflowStatusResponse,
    summary="Resume workflow execution",
    description="Resume a paused workflow"
)
async def resume_workflow(
    project_id: UUID,
    request: WorkflowResumeRequest,
    workflow_repo: WorkflowStateRepository = Depends(get_workflow_repo)
):
    """
    Resume a paused workflow.
    
    Args:
        project_id: Project UUID
        request: Resume request with optional notes
        workflow_repo: Workflow state repository
        
    Returns:
        Updated workflow state
        
    Raises:
        WorkflowNotFoundException: If no workflow found
    """
    # Get paused workflow
    workflow = await workflow_repo.get_by_project_and_status(
        str(project_id),
        "paused"
    )
    if not workflow:
        raise WorkflowNotFoundException(str(project_id))
    
    # Update workflow state
    updated = await workflow_repo.update(
        str(workflow.id),
        status="running"
    )
    
    # TODO: Signal Celery task to resume
    
    return WorkflowStatusResponse.model_validate(updated)


@router.get(
    "/{project_id}/status",
    response_model=WorkflowStatusResponse,
    summary="Get workflow status",
    description="Get current workflow execution status"
)
async def get_workflow_status(
    project_id: UUID,
    workflow_repo: WorkflowStateRepository = Depends(get_workflow_repo)
):
    """
    Get workflow status for a project.
    
    Args:
        project_id: Project UUID
        workflow_repo: Workflow state repository
        
    Returns:
        Current workflow state
        
    Raises:
        WorkflowNotFoundException: If no workflow found
    """
    # Get latest workflow (active or completed)
    workflow = await workflow_repo.get_latest_by_project(str(project_id))
    if not workflow:
        raise WorkflowNotFoundException(str(project_id))
    
    return WorkflowStatusResponse.model_validate(workflow)


@router.post(
    "/{project_id}/cancel",
    response_model=WorkflowStatusResponse,
    summary="Cancel workflow execution",
    description="Cancel a running or paused workflow"
)
async def cancel_workflow(
    project_id: UUID,
    workflow_repo: WorkflowStateRepository = Depends(get_workflow_repo)
):
    """
    Cancel workflow execution.
    
    Args:
        project_id: Project UUID
        workflow_repo: Workflow state repository
        
    Returns:
        Updated workflow state
        
    Raises:
        WorkflowNotRunningException: If no active workflow found
    """
    # Get active or paused workflow
    workflow = await workflow_repo.get_active_by_project(str(project_id))
    if not workflow:
        raise WorkflowNotRunningException(str(project_id))
    
    # Update workflow state
    updated = await workflow_repo.update(
        str(workflow.id),
        status="cancelled"
    )
    
    # TODO: Signal Celery task to cancel
    
    return WorkflowStatusResponse.model_validate(updated)

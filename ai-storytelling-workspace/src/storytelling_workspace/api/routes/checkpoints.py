"""Checkpoints management API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException

from ..schemas.checkpoint import (
    CheckpointResponse,
    CheckpointListResponse,
    CheckpointApprovalRequest,
    CheckpointRejectionRequest,
)
from ..dependencies import get_checkpoint_repo
from ...db.repositories.checkpoint import CheckpointRepository

router = APIRouter()


@router.get(
    "/",
    response_model=CheckpointListResponse,
    summary="List checkpoints",
    description="List checkpoints, optionally filtered by project"
)
async def list_checkpoints(
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    checkpoint_repo: CheckpointRepository = Depends(get_checkpoint_repo)
):
    if project_id:
        checkpoints = await checkpoint_repo.get_by_project_id(str(project_id))
    else:
        checkpoints = await checkpoint_repo.list(limit=100)
    
    # Calculate pending count using status value to handle string or Enum
    pending_count = 0
    for c in checkpoints:
        status_val = c.status.value if hasattr(c.status, 'value') else c.status
        if str(status_val).lower() == "pending":
            pending_count += 1
            
    return CheckpointListResponse(
        checkpoints=[CheckpointResponse.model_validate(c) for c in checkpoints],
        total=len(checkpoints),
        pending_count=pending_count
    )


@router.get(
    "/{checkpoint_id}",
    response_model=CheckpointResponse,
    summary="Get checkpoint by ID"
)
async def get_checkpoint(
    checkpoint_id: UUID,
    checkpoint_repo: CheckpointRepository = Depends(get_checkpoint_repo)
):
    checkpoint = await checkpoint_repo.get_by_id(str(checkpoint_id))
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    return CheckpointResponse.model_validate(checkpoint)


@router.post(
    "/{checkpoint_id}/approve",
    response_model=CheckpointResponse,
    summary="Approve checkpoint"
)
async def approve_checkpoint(
    checkpoint_id: UUID,
    request: CheckpointApprovalRequest,
    checkpoint_repo: CheckpointRepository = Depends(get_checkpoint_repo)
):
    checkpoint = await checkpoint_repo.approve(str(checkpoint_id), request.feedback)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    return CheckpointResponse.model_validate(checkpoint)


@router.post(
    "/{checkpoint_id}/reject",
    response_model=CheckpointResponse,
    summary="Reject checkpoint"
)
async def reject_checkpoint(
    checkpoint_id: UUID,
    request: CheckpointRejectionRequest,
    checkpoint_repo: CheckpointRepository = Depends(get_checkpoint_repo)
):
    checkpoint = await checkpoint_repo.reject(str(checkpoint_id), request.reason)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    return CheckpointResponse.model_validate(checkpoint)

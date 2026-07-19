"""Pydantic schemas for workflow management."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Request schemas
class WorkflowStartRequest(BaseModel):
    """Schema for starting a workflow."""
    
    resume_from_checkpoint: Optional[str] = Field(
        None,
        description="Checkpoint ID to resume from (optional)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_from_checkpoint": None
            }
        }
    }


class WorkflowPauseRequest(BaseModel):
    """Schema for pausing a workflow."""
    
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Reason for pausing (optional)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "reason": "User requested pause for review"
            }
        }
    }


class WorkflowResumeRequest(BaseModel):
    """Schema for resuming a workflow."""
    
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Notes about resumption (optional)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "notes": "Resuming after checkpoint approval"
            }
        }
    }


# Response schemas
class WorkflowStatusResponse(BaseModel):
    """Schema for workflow status response."""
    
    id: UUID = Field(..., description="Workflow UUID")
    project_id: UUID = Field(..., description="Project UUID")
    status: Literal[
        'running',
        'paused',
        'completed',
        'failed',
        'cancelled'
    ] = Field(..., description="Workflow status")
    current_phase: str = Field(..., description="Current workflow phase")
    current_agent: Optional[str] = Field(None, description="Currently executing agent")
    progress_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Progress percentage (0-100)"
    )
    completed_steps: int = Field(
        ...,
        ge=0,
        description="Number of completed steps"
    )
    total_steps: int = Field(
        ...,
        ge=1,
        description="Total number of steps"
    )
    started_at: datetime = Field(..., description="Workflow start time")
    paused_at: Optional[datetime] = Field(None, description="Pause time (if paused)")
    resumed_at: Optional[datetime] = Field(None, description="Resume time (if resumed)")
    completed_at: Optional[datetime] = Field(None, description="Completion time (if completed)")
    error_message: Optional[str] = Field(None, description="Error message (if failed)")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "status": "running",
                "current_phase": "drafting",
                "current_agent": "chapter_drafting",
                "progress_percentage": 45.5,
                "completed_steps": 7,
                "total_steps": 15,
                "started_at": "2024-01-01T00:00:00Z",
                "paused_at": None,
                "resumed_at": None,
                "completed_at": None,
                "error_message": None
            }
        }
    }


class WorkflowProgressUpdate(BaseModel):
    """Schema for real-time workflow progress updates (WebSocket)."""
    
    project_id: UUID = Field(..., description="Project UUID")
    workflow_id: UUID = Field(..., description="Workflow UUID")
    phase: str = Field(..., description="Current phase")
    agent: str = Field(..., description="Current agent")
    progress: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Progress percentage"
    )
    message: str = Field(..., description="Progress message")
    timestamp: datetime = Field(..., description="Update timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "workflow_id": "123e4567-e89b-12d3-a456-426614174000",
                "phase": "drafting",
                "agent": "chapter_drafting",
                "progress": 45.5,
                "message": "Drafting chapter 7 of 10",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    }


class WorkflowPhaseInfo(BaseModel):
    """Schema for workflow phase information."""
    
    phase_name: str = Field(..., description="Phase name")
    agents: list[str] = Field(..., description="Agents in this phase")
    estimated_duration_minutes: int = Field(
        ...,
        ge=1,
        description="Estimated duration in minutes"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "phase_name": "setup",
                "agents": ["intake", "concept", "worldbuilding", "character"],
                "estimated_duration_minutes": 10
            }
        }
    }


class WorkflowSummaryResponse(BaseModel):
    """Schema for workflow execution summary."""
    
    workflow_id: UUID = Field(..., description="Workflow UUID")
    project_id: UUID = Field(..., description="Project UUID")
    status: str = Field(..., description="Final status")
    total_duration_seconds: int = Field(
        ...,
        ge=0,
        description="Total execution time in seconds"
    )
    phases_completed: int = Field(..., ge=0, description="Number of phases completed")
    agents_executed: int = Field(..., ge=0, description="Number of agents executed")
    checkpoints_passed: int = Field(..., ge=0, description="Number of checkpoints passed")
    total_cost: float = Field(..., ge=0.0, description="Total API cost in USD")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "workflow_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "status": "completed",
                "total_duration_seconds": 2700,
                "phases_completed": 4,
                "agents_executed": 15,
                "checkpoints_passed": 6,
                "total_cost": 12.50
            }
        }
    }

"""Pydantic schemas for checkpoint management."""

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Request schemas
class CheckpointApprovalRequest(BaseModel):
    """Schema for approving a checkpoint."""
    
    feedback: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional feedback on the checkpoint"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "feedback": "Looks great! The character development is excellent."
            }
        }
    }


class CheckpointRejectionRequest(BaseModel):
    """Schema for rejecting a checkpoint."""
    
    reason: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Reason for rejection (required)"
    )
    feedback: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional feedback (optional)"
    )
    
    @field_validator('reason')
    @classmethod
    def reason_must_not_be_empty(cls, v: str) -> str:
        """Validate reason is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Reason cannot be empty or whitespace only')
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "reason": "The plot outline needs more conflict in Act 2",
                "feedback": "Consider adding a betrayal subplot to increase tension"
            }
        }
    }


# Response schemas
class CheckpointResponse(BaseModel):
    """Schema for checkpoint response."""
    
    id: UUID = Field(..., description="Checkpoint UUID")
    project_id: UUID = Field(..., description="Project UUID")
    story_bible_id: UUID = Field(..., description="Story Bible UUID")
    checkpoint_type: Literal[
        'concept',
        'characters',
        'outline',
        'chapter',
        'final'
    ] = Field(..., description="Type of checkpoint")
    phase: str = Field(..., description="Workflow phase")
    agent_name: str = Field(..., description="Agent that created checkpoint")
    status: Literal[
        'pending',
        'approved',
        'rejected',
        'skipped'
    ] = Field(..., description="Checkpoint status")
    content: dict[str, Any] = Field(..., description="Checkpoint content")
    changes: Optional[dict[str, Any]] = Field(
        None,
        description="Changes made by agent"
    )
    user_feedback: Optional[str] = Field(
        None,
        description="User feedback on checkpoint"
    )
    rejection_reason: Optional[str] = Field(
        None,
        description="Reason for rejection (if rejected)"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    reviewed_at: Optional[datetime] = Field(
        None,
        description="Review timestamp (if reviewed)"
    )
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "story_bible_id": "123e4567-e89b-12d3-a456-426614174002",
                "checkpoint_type": "outline",
                "phase": "architecture",
                "agent_name": "plot_architect",
                "status": "pending",
                "content": {
                    "outline": "Three-act structure with 25 chapters...",
                    "act_breaks": [8, 17]
                },
                "changes": {
                    "added": ["subplot_threads"],
                    "modified": ["chapter_count"]
                },
                "user_feedback": None,
                "rejection_reason": None,
                "created_at": "2024-01-01T00:00:00Z",
                "reviewed_at": None
            }
        }
    }


class CheckpointListResponse(BaseModel):
    """Schema for list of checkpoints."""
    
    checkpoints: list[CheckpointResponse] = Field(
        ...,
        description="List of checkpoints"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of checkpoints"
    )
    pending_count: int = Field(
        ...,
        ge=0,
        description="Number of pending checkpoints"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "checkpoints": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "project_id": "123e4567-e89b-12d3-a456-426614174001",
                        "story_bible_id": "123e4567-e89b-12d3-a456-426614174002",
                        "checkpoint_type": "outline",
                        "phase": "architecture",
                        "agent_name": "plot_architect",
                        "status": "pending",
                        "content": {},
                        "changes": None,
                        "user_feedback": None,
                        "rejection_reason": None,
                        "created_at": "2024-01-01T00:00:00Z",
                        "reviewed_at": None
                    }
                ],
                "total": 1,
                "pending_count": 1
            }
        }
    }


class CheckpointSummary(BaseModel):
    """Schema for checkpoint summary (lightweight)."""
    
    id: UUID = Field(..., description="Checkpoint UUID")
    checkpoint_type: str = Field(..., description="Type of checkpoint")
    status: str = Field(..., description="Checkpoint status")
    agent_name: str = Field(..., description="Agent name")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "checkpoint_type": "outline",
                "status": "approved",
                "agent_name": "plot_architect",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    }

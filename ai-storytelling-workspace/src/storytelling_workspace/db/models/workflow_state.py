"""
WorkflowState model for tracking workflow execution state.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, DECIMAL, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from storytelling_workspace.db.base import Base


class WorkflowStatus(str, Enum):
    """Workflow status enumeration."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowState(Base):
    """
    WorkflowState model for tracking workflow execution.
    
    Enables pause/resume functionality and progress tracking
    for long-running AI workflows.
    
    Attributes:
        id: UUID primary key
        project_id: Foreign key to Project
        current_phase: Current workflow phase
        current_agent: Current agent being executed
        status: Current workflow status
        total_steps: Total number of steps
        completed_steps: Number of completed steps
        progress_percentage: Progress as percentage
        state_data: Workflow state snapshot (JSON)
        error_message: Error message if failed
        error_stack: Error stack trace
        started_at: Workflow start timestamp
        paused_at: Workflow pause timestamp
        resumed_at: Workflow resume timestamp
        completed_at: Workflow completion timestamp
    
    Relationships:
        project: Many-to-one with Project
    """

    __tablename__ = "workflow_states"

    # Foreign keys
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Workflow state
    current_phase = Column(String(100), nullable=False)
    current_agent = Column(String(255), nullable=True)
    
    status = Column(
        SQLEnum(WorkflowStatus),
        default=WorkflowStatus.RUNNING,
        nullable=False,
        index=True,
    )
    
    # Progress tracking
    total_steps = Column(Integer, nullable=False)
    completed_steps = Column(Integer, default=0, nullable=False)
    progress_percentage = Column(DECIMAL(5, 2), default=Decimal("0.00"), nullable=False)
    
    # State snapshot (JSON for flexibility)
    state_data = Column(JSON, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_stack = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    paused_at = Column(DateTime, nullable=True)
    resumed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="workflow_states")
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<WorkflowState(id={self.id}, phase={self.current_phase}, "
            f"status={self.status}, progress={self.progress_percentage}%)>"
        )
    
    def update_progress(self, completed_steps: int) -> None:
        """
        Update workflow progress.
        
        Args:
            completed_steps: Number of completed steps
        """
        self.completed_steps = completed_steps
        if self.total_steps > 0:
            self.progress_percentage = Decimal(
                str(round((completed_steps / self.total_steps) * 100, 2))
            )
    
    def pause(self) -> None:
        """Pause the workflow."""
        self.status = WorkflowStatus.PAUSED
        self.paused_at = datetime.utcnow()
    
    def resume(self) -> None:
        """Resume the workflow."""
        self.status = WorkflowStatus.RUNNING
        self.resumed_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark workflow as completed."""
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = Decimal("100.00")
    
    def fail(self, error_message: str, error_stack: str | None = None) -> None:
        """
        Mark workflow as failed.
        
        Args:
            error_message: Error message
            error_stack: Optional error stack trace
        """
        self.status = WorkflowStatus.FAILED
        self.error_message = error_message
        self.error_stack = error_stack
        self.completed_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel the workflow."""
        self.status = WorkflowStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    @property
    def is_running(self) -> bool:
        """Check if workflow is running."""
        return self.status == WorkflowStatus.RUNNING
    
    @property
    def is_paused(self) -> bool:
        """Check if workflow is paused."""
        return self.status == WorkflowStatus.PAUSED
    
    @property
    def is_completed(self) -> bool:
        """Check if workflow is completed."""
        return self.status == WorkflowStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if workflow failed."""
        return self.status == WorkflowStatus.FAILED
    
    @property
    def duration_seconds(self) -> int | None:
        """Calculate workflow duration in seconds."""
        if self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None
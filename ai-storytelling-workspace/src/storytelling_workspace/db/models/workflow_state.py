"""WorkflowState model - tracks workflow execution state."""
from decimal import Decimal
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, Integer, JSON, Numeric, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storytelling_workspace.db.base import Base, TimestampMixin, UUIDMixin


class WorkflowState(Base, UUIDMixin, TimestampMixin):
    """
    WorkflowState model for tracking workflow execution.
    
    Enables pause/resume functionality and progress tracking.
    """
    
    __tablename__ = "workflow_states"
    
    # Foreign Keys
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Project ID"
    )
    
    # Workflow State
    current_phase: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Current workflow phase"
    )
    
    current_agent: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Currently executing agent"
    )
    
    status: Mapped[str] = mapped_column(
        Enum(
            "running",
            "paused",
            "completed",
            "failed",
            "cancelled",
            name="workflow_status"
        ),
        default="running",
        nullable=False,
        index=True,
        comment="Workflow status"
    )
    
    # Progress Tracking
    total_steps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Total workflow steps"
    )
    
    completed_steps: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Completed steps"
    )
    
    progress_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Progress percentage (0-100)"
    )
    
    # State Snapshot (JSON)
    state_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Workflow state for resume"
    )
    
    # Error Tracking
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if failed"
    )
    
    error_stack: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error stack trace"
    )
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Workflow start time"
    )
    
    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="When workflow was paused"
    )
    
    resumed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="When workflow was resumed"
    )
    
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="When workflow completed"
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="workflow_states"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<WorkflowState(id={self.id}, status={self.status}, progress={self.progress_percentage}%)>"

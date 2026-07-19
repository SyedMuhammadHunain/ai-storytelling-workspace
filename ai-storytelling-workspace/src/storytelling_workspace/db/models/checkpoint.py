"""
Checkpoint model for workflow checkpoints and user review.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from storytelling_workspace.db.base import Base


class CheckpointType(str, Enum):
    """Checkpoint type enumeration."""

    CONCEPT = "concept"
    CHARACTERS = "characters"
    OUTLINE = "outline"
    CHAPTER = "chapter"
    FINAL = "final"


class CheckpointStatus(str, Enum):
    """Checkpoint status enumeration."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"


class Checkpoint(Base):
    """
    Checkpoint model for workflow review points.
    
    Captures Story Bible state at critical workflow points
    for user review and approval.
    
    Attributes:
        id: UUID primary key
        project_id: Foreign key to Project
        story_bible_id: Foreign key to StoryBible
        checkpoint_type: Type of checkpoint
        phase: Workflow phase name
        agent_name: Name of agent that created checkpoint
        status: Current checkpoint status
        content: Content snapshot (JSON)
        changes: Changes made since last checkpoint (JSON)
        user_feedback: User feedback text
        rejection_reason: Reason for rejection
        created_at: Creation timestamp
        reviewed_at: Review timestamp
    
    Relationships:
        project: Many-to-one with Project
        story_bible: Many-to-one with StoryBible
    """

    __tablename__ = "checkpoints"

    # Foreign keys
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    story_bible_id = Column(
        String(36),
        ForeignKey("story_bibles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Checkpoint metadata
    checkpoint_type = Column(
        SQLEnum(CheckpointType),
        nullable=False,
        index=True,
    )
    
    phase = Column(String(100), nullable=False)
    agent_name = Column(String(255), nullable=False)
    
    # Checkpoint state
    status = Column(
        SQLEnum(CheckpointStatus),
        default=CheckpointStatus.PENDING,
        nullable=False,
        index=True,
    )
    
    # Content snapshot (JSON for flexibility)
    content = Column(JSON, nullable=False)
    changes = Column(JSON, nullable=True)
    
    # User feedback
    user_feedback = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="checkpoints")
    story_bible = relationship("StoryBible", back_populates="checkpoints")
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Checkpoint(id={self.id}, type={self.checkpoint_type}, "
            f"status={self.status})>"
        )
    
    def approve(self, feedback: str | None = None) -> None:
        """
        Approve the checkpoint.
        
        Args:
            feedback: Optional user feedback
        """
        self.status = CheckpointStatus.APPROVED
        self.reviewed_at = datetime.utcnow()
        if feedback:
            self.user_feedback = feedback
    
    def reject(self, reason: str) -> None:
        """
        Reject the checkpoint.
        
        Args:
            reason: Reason for rejection
        """
        self.status = CheckpointStatus.REJECTED
        self.reviewed_at = datetime.utcnow()
        self.rejection_reason = reason
    
    def skip(self) -> None:
        """Skip the checkpoint."""
        self.status = CheckpointStatus.SKIPPED
        self.reviewed_at = datetime.utcnow()
    
    @property
    def is_pending(self) -> bool:
        """Check if checkpoint is pending review."""
        return self.status == CheckpointStatus.PENDING
    
    @property
    def is_approved(self) -> bool:
        """Check if checkpoint is approved."""
        return self.status == CheckpointStatus.APPROVED
    
    @property
    def is_rejected(self) -> bool:
        """Check if checkpoint is rejected."""
        return self.status == CheckpointStatus.REJECTED
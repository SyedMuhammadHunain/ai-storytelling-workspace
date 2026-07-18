"""Checkpoint model - workflow checkpoints for user review."""
from sqlalchemy import Enum, ForeignKey, JSON, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storytelling_workspace.db.base import Base, TimestampMixin, UUIDMixin


class Checkpoint(Base, UUIDMixin, TimestampMixin):
    """
    Checkpoint model for workflow review points.
    
    Captures state at critical workflow points for user approval.
    """
    
    __tablename__ = "checkpoints"
    
    # Foreign Keys
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Project ID"
    )
    
    story_bible_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("story_bibles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Story Bible ID"
    )
    
    # Checkpoint Metadata
    checkpoint_type: Mapped[str] = mapped_column(
        Enum(
            "concept",
            "characters",
            "outline",
            "chapter",
            "final",
            name="checkpoint_type"
        ),
        nullable=False,
        index=True,
        comment="Type of checkpoint"
    )
    
    phase: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Workflow phase name"
    )
    
    agent_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Agent that created checkpoint"
    )
    
    # Checkpoint State
    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "approved",
            "rejected",
            "skipped",
            name="checkpoint_status"
        ),
        default="pending",
        nullable=False,
        index=True,
        comment="Checkpoint status"
    )
    
    # Content Snapshot (JSON)
    content: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Checkpoint content snapshot"
    )
    
    changes: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Changes made since last checkpoint"
    )
    
    # User Feedback
    user_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User feedback on checkpoint"
    )
    
    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for rejection"
    )
    
    reviewed_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="When user reviewed checkpoint"
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="checkpoints"
    )
    
    story_bible: Mapped["StoryBible"] = relationship(
        "StoryBible",
        back_populates="checkpoints"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Checkpoint(id={self.id}, type={self.checkpoint_type}, status={self.status})>"

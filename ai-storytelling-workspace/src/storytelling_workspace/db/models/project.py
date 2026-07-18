"""Project model - root entity for storytelling projects."""
from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storytelling_workspace.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class Project(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Project model representing a book/novel project.
    
    A project is the root entity that contains:
    - Story Bibles (versioned)
    - Checkpoints (for user review)
    - Images (cover art, portraits, scenes)
    - Workflow states (for pause/resume)
    - API costs (for billing)
    """
    
    __tablename__ = "projects"
    
    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Project name"
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Project description"
    )
    
    genre: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Book genre (e.g., Fantasy, Sci-Fi)"
    )
    
    target_length: Mapped[int] = mapped_column(
        Integer,
        default=80000,
        nullable=False,
        comment="Target word count"
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        Enum(
            "draft",
            "in_progress",
            "paused",
            "completed",
            "archived",
            name="project_status"
        ),
        default="draft",
        nullable=False,
        comment="Project status"
    )
    
    # Relationships
    story_bibles: Mapped[list["StoryBible"]] = relationship(
        "StoryBible",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    checkpoints: Mapped[list["Checkpoint"]] = relationship(
        "Checkpoint",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    images: Mapped[list["Image"]] = relationship(
        "Image",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    workflow_states: Mapped[list["WorkflowState"]] = relationship(
        "WorkflowState",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    api_costs: Mapped[list["APICost"]] = relationship(
        "APICost",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"

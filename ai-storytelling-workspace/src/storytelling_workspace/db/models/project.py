"""
Project model for storing project metadata and configuration.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.orm import relationship

from storytelling_workspace.db.base import Base


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    """
    Project model representing a book writing project.
    
    Attributes:
        id: UUID primary key
        name: Project name
        description: Project description
        genre: Book genre
        target_length: Target word count (default 80,000)
        status: Current project status
        created_at: Creation timestamp
        updated_at: Last update timestamp
        deleted_at: Soft delete timestamp
    
    Relationships:
        story_bibles: One-to-many with StoryBible (versioned)
        checkpoints: One-to-many with Checkpoint
        images: One-to-many with Image
        workflow_states: One-to-many with WorkflowState
        api_costs: One-to-many with APICost
    """

    __tablename__ = "projects"

    # Core fields
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    genre = Column(String(100), nullable=True)
    target_length = Column(Integer, default=80000, nullable=False)
    
    # Status
    status = Column(
        SQLEnum(ProjectStatus),
        nullable=False,
        index=True,
        server_default="draft",
    )
    
    def __init__(self, **kwargs):
        """Initialize with default status if not provided."""
        if 'status' not in kwargs:
            kwargs['status'] = ProjectStatus.DRAFT
        super().__init__(**kwargs)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    # Relationships
    story_bibles = relationship(
        "StoryBible",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    checkpoints = relationship(
        "Checkpoint",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    images = relationship(
        "Image",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    workflow_states = relationship(
        "WorkflowState",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    api_costs = relationship(
        "APICost",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        """String representation."""
        status_value = self.status.value if self.status else None
        return f"<Project(id={self.id}, name={self.name}, status={status_value})>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if project is soft deleted."""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """Soft delete the project."""
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft deleted project."""
        self.deleted_at = None
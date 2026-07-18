"""StoryBible model - versioned story bible state with JSON storage."""
from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storytelling_workspace.db.base import Base, TimestampMixin, UUIDMixin


class StoryBible(Base, UUIDMixin, TimestampMixin):
    """
    StoryBible model representing versioned story bible state.
    
    Stores the complete Story Bible as JSON for flexibility.
    Each version is a snapshot that can be rolled back to.
    """
    
    __tablename__ = "story_bibles"
    
    # Foreign Keys
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Project ID"
    )
    
    # Version Control
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Version number for rollback"
    )
    
    # Core Story Bible Sections (JSON)
    brief: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Book brief and high-level concept"
    )
    
    concept: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Detailed concept and themes"
    )
    
    world_rules: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="World building rules and constraints"
    )
    
    characters: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Character profiles and relationships"
    )
    
    locations: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Location descriptions"
    )
    
    timeline: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Story timeline and events"
    )
    
    plot_threads: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Plot threads and arcs"
    )
    
    # Metadata
    terminology: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Custom terminology and glossary"
    )
    
    style_guide: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Writing style guidelines"
    )
    
    additional_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional metadata"
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="story_bibles"
    )
    
    chapters: Mapped[list["Chapter"]] = relationship(
        "Chapter",
        back_populates="story_bible",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    checkpoints: Mapped[list["Checkpoint"]] = relationship(
        "Checkpoint",
        back_populates="story_bible",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    images: Mapped[list["Image"]] = relationship(
        "Image",
        back_populates="story_bible",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    agent_deltas: Mapped[list["AgentDelta"]] = relationship(
        "AgentDelta",
        back_populates="story_bible",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<StoryBible(id={self.id}, project_id={self.project_id}, version={self.version})>"

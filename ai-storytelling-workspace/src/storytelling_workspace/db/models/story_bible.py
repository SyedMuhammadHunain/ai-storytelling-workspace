"""
StoryBible model for storing complete Story Bible state with versioning.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from storytelling_workspace.db.base import Base


class StoryBible(Base):
    """
    StoryBible model representing the complete story state.
    
    Stores all Story Bible sections as JSON for flexibility.
    Supports versioning for rollback capability.
    
    Attributes:
        id: UUID primary key
        project_id: Foreign key to Project
        version: Version number (increments on updates)
        brief: Initial project brief (JSON)
        concept: Story concept and themes (JSON)
        world_rules: World-building rules and constraints (JSON)
        characters: Character profiles and arcs (JSON)
        locations: Setting and location details (JSON)
        timeline: Story timeline and chronology (JSON)
        plot_threads: Plot threads and story arcs (JSON)
        terminology: Custom terminology and glossary (JSON)
        style_guide: Writing style guidelines (JSON)
        metadata: Additional metadata (JSON)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Relationships:
        project: Many-to-one with Project
        chapters: One-to-many with Chapter
        checkpoints: One-to-many with Checkpoint
        images: One-to-many with Image
        agent_deltas: One-to-many with AgentDelta
    """

    __tablename__ = "story_bibles"

    # Foreign keys
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Version tracking
    version = Column(Integer, default=1, nullable=False)
    
    # Core Story Bible sections (JSON for flexibility)
    brief = Column(JSON, nullable=True)
    concept = Column(JSON, nullable=True)
    world_rules = Column(JSON, nullable=True)
    characters = Column(JSON, nullable=True)
    locations = Column(JSON, nullable=True)
    timeline = Column(JSON, nullable=True)
    plot_threads = Column(JSON, nullable=True)
    
    # Metadata sections
    terminology = Column(JSON, nullable=True)
    style_guide = Column(JSON, nullable=True)
    story_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Relationships
    project = relationship("Project", back_populates="story_bibles")
    
    chapters = relationship(
        "Chapter",
        back_populates="story_bible",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    checkpoints = relationship(
        "Checkpoint",
        back_populates="story_bible",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    images = relationship(
        "Image",
        back_populates="story_bible",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    agent_deltas = relationship(
        "AgentDelta",
        back_populates="story_bible",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<StoryBible(id={self.id}, project_id={self.project_id}, version={self.version})>"
    
    def increment_version(self) -> None:
        """Increment the version number."""
        self.version += 1
    
    def get_section(self, section_name: str) -> dict | None:
        """
        Get a specific Story Bible section.
        
        Args:
            section_name: Name of the section (e.g., 'characters', 'plot_threads')
        
        Returns:
            Section data as dict or None if not found
        """
        return getattr(self, section_name, None)
    
    def update_section(self, section_name: str, data: dict) -> None:
        """
        Update a specific Story Bible section.
        
        Args:
            section_name: Name of the section to update
            data: New data for the section
        """
        if hasattr(self, section_name):
            setattr(self, section_name, data)
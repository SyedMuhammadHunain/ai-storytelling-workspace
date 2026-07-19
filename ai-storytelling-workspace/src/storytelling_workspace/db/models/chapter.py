"""
Chapter model for storing individual chapter data.
"""

from enum import Enum

from sqlalchemy import Column, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from storytelling_workspace.db.base import Base


class ChapterStatus(str, Enum):
    """Chapter status enumeration."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVISED = "revised"


class Chapter(Base):
    """
    Chapter model for individual book chapters.
    
    Attributes:
        id: UUID primary key
        story_bible_id: Foreign key to StoryBible
        chapter_number: Chapter number (1-based)
        title: Chapter title
        content: Chapter content (LONGTEXT)
        summary: Chapter summary
        pov: Point of view character
        word_count: Actual word count
        target_word_count: Target word count
        status: Current chapter status
        goal: Chapter goal
        conflict: Chapter conflict
        resolution: Chapter resolution
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Relationships:
        story_bible: Many-to-one with StoryBible
    """

    __tablename__ = "chapters"

    # Foreign keys
    story_bible_id = Column(
        String(36),
        ForeignKey("story_bibles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Chapter metadata
    chapter_number = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    
    # Chapter content
    content = Column(Text, nullable=True)  # LONGTEXT in MySQL
    summary = Column(Text, nullable=True)
    pov = Column(String(255), nullable=True)
    
    # Metadata
    word_count = Column(Integer, default=0, nullable=False)
    target_word_count = Column(Integer, default=3000, nullable=False)
    
    status = Column(
        SQLEnum(ChapterStatus),
        default=ChapterStatus.PLANNED,
        nullable=False,
        index=True,
    )
    
    # Story structure
    goal = Column(Text, nullable=True)
    conflict = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    
    # Relationships
    story_bible = relationship("StoryBible", back_populates="chapters")
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Chapter(id={self.id}, number={self.chapter_number}, "
            f"title={self.title}, status={self.status})>"
        )
    
    def update_word_count(self) -> None:
        """Update word count from content."""
        if self.content:
            self.word_count = len(self.content.split())
        else:
            self.word_count = 0
    
    @property
    def is_completed(self) -> bool:
        """Check if chapter is completed."""
        return self.status == ChapterStatus.COMPLETED
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress as percentage of target word count."""
        if self.target_word_count > 0:
            return min(100.0, (self.word_count / self.target_word_count) * 100)
        return 0.0
"""Chapter model - individual chapter content and metadata."""
from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storytelling_workspace.db.base import Base, TimestampMixin, UUIDMixin


class Chapter(Base, UUIDMixin, TimestampMixin):
    """
    Chapter model representing individual chapter data.
    
    Stores chapter content, metadata, and story structure elements.
    """
    
    __tablename__ = "chapters"
    
    # Foreign Keys
    story_bible_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("story_bibles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Story Bible ID"
    )
    
    # Chapter Information
    chapter_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Chapter number (1-based)"
    )
    
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Chapter title"
    )
    
    # Chapter Content
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Full chapter text"
    )
    
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Chapter summary"
    )
    
    pov: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Point of view character"
    )
    
    # Metadata
    word_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Actual word count"
    )
    
    target_word_count: Mapped[int] = mapped_column(
        Integer,
        default=3000,
        nullable=False,
        comment="Target word count"
    )
    
    status: Mapped[str] = mapped_column(
        Enum(
            "planned",
            "in_progress",
            "completed",
            "revised",
            name="chapter_status"
        ),
        default="planned",
        nullable=False,
        index=True,
        comment="Chapter status"
    )
    
    # Story Structure
    goal: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Chapter goal"
    )
    
    conflict: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Main conflict"
    )
    
    resolution: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Conflict resolution"
    )
    
    # Relationships
    story_bible: Mapped["StoryBible"] = relationship(
        "StoryBible",
        back_populates="chapters"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Chapter(id={self.id}, number={self.chapter_number}, title={self.title})>"

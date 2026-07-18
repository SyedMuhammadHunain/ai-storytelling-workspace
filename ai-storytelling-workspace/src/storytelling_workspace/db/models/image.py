"""Image model - metadata for generated images."""
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storytelling_workspace.db.base import Base, TimestampMixin, UUIDMixin


class Image(Base, UUIDMixin, TimestampMixin):
    """
    Image model for generated image metadata.
    
    Tracks cover art, character portraits, and scene illustrations.
    """
    
    __tablename__ = "images"
    
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
    
    # Image Metadata
    image_type: Mapped[str] = mapped_column(
        Enum(
            "cover_art",
            "character_portrait",
            "scene_illustration",
            name="image_type"
        ),
        nullable=False,
        index=True,
        comment="Type of image"
    )
    
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Relative path to image file"
    )
    
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="File size in bytes"
    )
    
    # Generation Details
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Prompt used to generate image"
    )
    
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="AI model used"
    )
    
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="AI provider (mistral, openai)"
    )
    
    # Image Properties
    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Image width in pixels"
    )
    
    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Image height in pixels"
    )
    
    format: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Image format (png, jpg, webp)"
    )
    
    # Associated Entity
    character_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="For character portraits"
    )
    
    chapter_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="For scene illustrations"
    )
    
    # Cost Tracking
    generation_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        default=Decimal("0.0000"),
        nullable=False,
        comment="Cost in USD"
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="images"
    )
    
    story_bible: Mapped["StoryBible"] = relationship(
        "StoryBible",
        back_populates="images"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Image(id={self.id}, type={self.image_type}, path={self.file_path})>"

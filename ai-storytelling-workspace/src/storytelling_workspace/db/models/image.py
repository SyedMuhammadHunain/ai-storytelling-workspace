"""
Image model for storing generated image metadata.
"""

from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, DECIMAL, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from storytelling_workspace.db.base import Base


class ImageType(str, Enum):
    """Image type enumeration."""

    COVER_ART = "cover_art"
    CHARACTER_PORTRAIT = "character_portrait"
    SCENE_ILLUSTRATION = "scene_illustration"


class Image(Base):
    """
    Image model for generated images (cover art, portraits, scenes).
    
    Attributes:
        id: UUID primary key
        project_id: Foreign key to Project
        story_bible_id: Foreign key to StoryBible
        image_type: Type of image
        file_path: Path to image file
        file_size: File size in bytes
        prompt: Generation prompt
        model: AI model used
        provider: AI provider (mistral, openai)
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (png, jpg, webp)
        character_name: Associated character (for portraits)
        chapter_number: Associated chapter (for scenes)
        generation_cost: Cost of generation
        created_at: Creation timestamp
    
    Relationships:
        project: Many-to-one with Project
        story_bible: Many-to-one with StoryBible
    """

    __tablename__ = "images"

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
    
    # Image metadata
    image_type = Column(
        String(50),  # Using String instead of Enum for flexibility
        nullable=False,
        index=True,
    )
    
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    
    # Generation details
    prompt = Column(Text, nullable=False)
    model = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    
    # Image properties
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    format = Column(String(10), nullable=False)  # png, jpg, webp
    
    # Associated entity
    character_name = Column(String(255), nullable=True, index=True)
    chapter_number = Column(Integer, nullable=True, index=True)
    
    # Cost tracking
    generation_cost = Column(DECIMAL(10, 4), default=Decimal("0.0000"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="images")
    story_bible = relationship("StoryBible", back_populates="images")
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Image(id={self.id}, type={self.image_type}, "
            f"file_path={self.file_path})>"
        )
    
    @property
    def is_cover_art(self) -> bool:
        """Check if image is cover art."""
        return self.image_type == ImageType.COVER_ART.value
    
    @property
    def is_character_portrait(self) -> bool:
        """Check if image is character portrait."""
        return self.image_type == ImageType.CHARACTER_PORTRAIT.value
    
    @property
    def is_scene_illustration(self) -> bool:
        """Check if image is scene illustration."""
        return self.image_type == ImageType.SCENE_ILLUSTRATION.value
    
    @property
    def dimensions(self) -> tuple[int, int]:
        """Get image dimensions as tuple."""
        return (self.width, self.height)
    
    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)
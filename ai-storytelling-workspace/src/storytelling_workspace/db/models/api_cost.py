"""
APICost model for tracking API usage and costs.
"""

from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, Column, DECIMAL, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from storytelling_workspace.db.base import Base


class APIType(str, Enum):
    """API type enumeration."""

    TEXT = "text"
    IMAGE = "image"


class APICost(Base):
    """
    APICost model for tracking API usage and costs.
    
    Provides granular cost tracking per API call for billing
    and usage analytics.
    
    Attributes:
        id: UUID primary key
        project_id: Foreign key to Project
        provider: AI provider (mistral, openai)
        model: Model name
        api_type: Type of API call (text, image)
        tokens_used: Number of tokens used (for text)
        images_generated: Number of images generated
        cost: Cost of the API call
        success: Whether the call succeeded
        error_message: Error message if failed
        created_at: Creation timestamp
    
    Relationships:
        project: Many-to-one with Project
    """

    __tablename__ = "api_costs"

    # Foreign keys
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # API details
    provider = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    api_type = Column(
        SQLEnum(APIType),
        nullable=False,
        index=True,
    )
    
    # Usage metrics
    tokens_used = Column(Integer, nullable=True)
    images_generated = Column(Integer, nullable=True)
    cost = Column(DECIMAL(10, 4), nullable=False)
    
    # Request details
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="api_costs")
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<APICost(id={self.id}, provider={self.provider}, "
            f"model={self.model}, cost=${self.cost})>"
        )
    
    @property
    def is_text_api(self) -> bool:
        """Check if this is a text API call."""
        return self.api_type == APIType.TEXT
    
    @property
    def is_image_api(self) -> bool:
        """Check if this is an image API call."""
        return self.api_type == APIType.IMAGE
    
    @property
    def cost_per_token(self) -> Decimal | None:
        """Calculate cost per token for text APIs."""
        if self.is_text_api and self.tokens_used and self.tokens_used > 0:
            return self.cost / Decimal(str(self.tokens_used))
        return None
    
    @property
    def cost_per_image(self) -> Decimal | None:
        """Calculate cost per image for image APIs."""
        if self.is_image_api and self.images_generated and self.images_generated > 0:
            return self.cost / Decimal(str(self.images_generated))
        return None
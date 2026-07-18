"""APICost model - tracks API usage and costs."""
from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storytelling_workspace.db.base import Base, TimestampMixin, UUIDMixin


class APICost(Base, UUIDMixin, TimestampMixin):
    """
    APICost model for tracking API usage and costs.
    
    Supports billing and usage analytics.
    """
    
    __tablename__ = "api_costs"
    
    # Foreign Keys
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Project ID"
    )
    
    # API Details
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="AI provider (mistral, openai)"
    )
    
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Model name"
    )
    
    api_type: Mapped[str] = mapped_column(
        Enum(
            "text",
            "image",
            name="api_type"
        ),
        nullable=False,
        index=True,
        comment="API type"
    )
    
    # Usage Metrics
    tokens_used: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="For text generation"
    )
    
    images_generated: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="For image generation"
    )
    
    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        comment="Cost in USD"
    )
    
    # Request Details
    success: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether request succeeded"
    )
    
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if failed"
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="api_costs"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<APICost(id={self.id}, provider={self.provider}, cost=${self.cost})>"

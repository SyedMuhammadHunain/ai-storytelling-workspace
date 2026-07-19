"""
Database base configuration and declarative base.

This module provides the SQLAlchemy declarative base and common
base model functionality for all database models.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import DeclarativeMeta


class CustomBase:
    """Base class for all database models with common functionality."""

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name (lowercase)."""
        return cls.__name__.lower()

    # Primary key (UUID)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"


# Create declarative base with custom base class
Base: DeclarativeMeta = declarative_base(cls=CustomBase)


# Import all models here to ensure they're registered with Base
# This is used by Alembic for auto-generating migrations
def import_models() -> None:
    """Import all models to register them with SQLAlchemy Base."""
    from storytelling_workspace.db.models import (  # noqa: F401
        agent_delta,
        api_cost,
        chapter,
        checkpoint,
        image,
        project,
        story_bible,
        workflow_state,
    )
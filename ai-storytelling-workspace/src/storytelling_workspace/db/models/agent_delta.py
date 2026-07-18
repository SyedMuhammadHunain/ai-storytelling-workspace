"""AgentDelta model - audit trail of agent changes."""
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storytelling_workspace.db.base import Base, TimestampMixin, UUIDMixin


class AgentDelta(Base, UUIDMixin, TimestampMixin):
    """
    AgentDelta model for tracking agent changes.
    
    Provides complete audit trail of all AI agent actions.
    """
    
    __tablename__ = "agent_deltas"
    
    # Foreign Keys
    story_bible_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("story_bibles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Story Bible ID"
    )
    
    # Agent Information
    agent_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Agent name"
    )
    
    agent_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Agent version for tracking"
    )
    
    # Change Details
    changes: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Changes made by agent"
    )
    
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable summary"
    )
    
    # Metadata
    execution_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Agent execution time in milliseconds"
    )
    
    tokens_used: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Tokens consumed"
    )
    
    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        default=Decimal("0.0000"),
        nullable=False,
        comment="Cost in USD"
    )
    
    # Relationships
    story_bible: Mapped["StoryBible"] = relationship(
        "StoryBible",
        back_populates="agent_deltas"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<AgentDelta(id={self.id}, agent={self.agent_name}, cost=${self.cost})>"

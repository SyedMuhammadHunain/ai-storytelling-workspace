"""
AgentDelta model for audit trail of agent changes.
"""

from decimal import Decimal

from sqlalchemy import Column, DECIMAL, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from storytelling_workspace.db.base import Base


class AgentDelta(Base):
    """
    AgentDelta model for tracking agent changes to Story Bible.
    
    Provides complete audit trail of all AI agent actions
    with cost tracking and performance metrics.
    
    Attributes:
        id: UUID primary key
        story_bible_id: Foreign key to StoryBible
        agent_name: Name of the agent
        agent_version: Version of the agent
        changes: Changes made (JSON)
        summary: Summary of changes
        execution_time_ms: Execution time in milliseconds
        tokens_used: Number of tokens used
        cost: Cost of execution
        created_at: Creation timestamp
    
    Relationships:
        story_bible: Many-to-one with StoryBible
    """

    __tablename__ = "agent_deltas"

    # Foreign keys
    story_bible_id = Column(
        String(36),
        ForeignKey("story_bibles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Agent information
    agent_name = Column(String(255), nullable=False, index=True)
    agent_version = Column(String(50), nullable=True)
    
    # Change details
    changes = Column(JSON, nullable=False)
    summary = Column(Text, nullable=True)
    
    # Metadata
    execution_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(DECIMAL(10, 4), default=Decimal("0.0000"), nullable=False)
    
    # Relationships
    story_bible = relationship("StoryBible", back_populates="agent_deltas")
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<AgentDelta(id={self.id}, agent={self.agent_name}, "
            f"cost=${self.cost})>"
        )
    
    @property
    def execution_time_seconds(self) -> float | None:
        """Get execution time in seconds."""
        if self.execution_time_ms is not None:
            return self.execution_time_ms / 1000.0
        return None
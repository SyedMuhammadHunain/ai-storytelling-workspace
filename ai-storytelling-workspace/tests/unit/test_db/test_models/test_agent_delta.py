"""
Unit tests for AgentDelta model.
"""

import pytest
from decimal import Decimal

from storytelling_workspace.db.models import AgentDelta


def test_agent_delta_creation():
    """Test creating an AgentDelta instance."""
    delta = AgentDelta(
        story_bible_id="test-bible-id",
        agent_name="ConceptAgent",
        agent_version="1.0.0",
        changes={"added": ["theme1", "theme2"]},
        summary="Added two themes",
        execution_time_ms=1500,
        tokens_used=250,
        cost=Decimal("0.0025"),
    )
    
    assert delta.story_bible_id == "test-bible-id"
    assert delta.agent_name == "ConceptAgent"
    assert delta.agent_version == "1.0.0"
    assert delta.changes == {"added": ["theme1", "theme2"]}
    assert delta.summary == "Added two themes"
    assert delta.execution_time_ms == 1500
    assert delta.tokens_used == 250
    assert delta.cost == Decimal("0.0025")


def test_agent_delta_execution_time_seconds():
    """Test execution_time_seconds property."""
    delta = AgentDelta(
        story_bible_id="test-id",
        agent_name="TestAgent",
        changes={},
        execution_time_ms=2500,
    )
    
    assert delta.execution_time_seconds == 2.5
    
    delta_no_time = AgentDelta(
        story_bible_id="test-id",
        agent_name="TestAgent",
        changes={},
        execution_time_ms=None,
    )
    
    assert delta_no_time.execution_time_seconds is None


def test_agent_delta_repr():
    """Test string representation."""
    delta = AgentDelta(
        story_bible_id="test-id",
        agent_name="CharacterAgent",
        changes={},
        cost=Decimal("0.0150"),
    )
    
    repr_str = repr(delta)
    
    assert "AgentDelta" in repr_str
    assert "CharacterAgent" in repr_str
    assert "0.0150" in repr_str

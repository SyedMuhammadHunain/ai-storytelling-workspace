"""Tests for Worldbuilding Agent."""

import pytest
from storytelling_workspace.agents.worldbuilding import WorldbuildingAgent
from storytelling_workspace.story_bible import StoryBible


def test_worldbuilding_agent_initialization():
    """Test WorldbuildingAgent can be initialized."""
    agent = WorldbuildingAgent()
    
    assert agent.name == "Worldbuilding Agent"


def test_worldbuilding_agent_execute():
    """Test WorldbuildingAgent executes and creates world."""
    agent = WorldbuildingAgent()
    bible = StoryBible(project_name="Test")
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "world_rules" in result
    assert result["locations_count"] > 0
    assert result["timeline_events_count"] > 0


def test_worldbuilding_agent_updates_world_rules():
    """Test WorldbuildingAgent updates Story Bible with world rules."""
    agent = WorldbuildingAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert bible.world_rules.magic_system != ""
    assert bible.world_rules.technology_level != ""
    assert bible.world_rules.social_structure != ""
    assert len(bible.world_rules.key_rules) > 0


def test_worldbuilding_agent_creates_locations():
    """Test WorldbuildingAgent creates locations."""
    agent = WorldbuildingAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.locations) > 0
    for location in bible.locations.values():
        assert location.name != ""
        assert location.description != ""


def test_worldbuilding_agent_creates_timeline():
    """Test WorldbuildingAgent creates timeline events."""
    agent = WorldbuildingAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.timeline) > 0
    for event in bible.timeline:
        assert event.timestamp != ""
        assert event.event != ""


def test_worldbuilding_agent_records_changes():
    """Test WorldbuildingAgent records changes to Story Bible."""
    agent = WorldbuildingAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.deltas) == 1
    assert bible.deltas[0].agent_name == "Worldbuilding Agent"
    assert "world" in bible.deltas[0].summary.lower()


def test_worldbuilding_agent_increments_version():
    """Test WorldbuildingAgent increments Story Bible version."""
    agent = WorldbuildingAgent()
    bible = StoryBible(project_name="Test")
    initial_version = bible.version
    
    agent.execute(bible)
    
    assert bible.version > initial_version

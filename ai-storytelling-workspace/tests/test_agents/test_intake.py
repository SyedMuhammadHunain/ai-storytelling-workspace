"""Tests for Intake Agent."""

import pytest
from storytelling_workspace.agents.intake import IntakeAgent
from storytelling_workspace.story_bible import StoryBible


def test_intake_agent_initialization():
    """Test IntakeAgent can be initialized."""
    agent = IntakeAgent()
    
    assert agent.name == "Intake Agent"


def test_intake_agent_execute():
    """Test IntakeAgent executes and creates book brief."""
    agent = IntakeAgent()
    bible = StoryBible(project_name="Test")
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "brief" in result
    assert bible.brief.genre == "Fantasy"
    assert bible.brief.target_length == 80000


def test_intake_agent_updates_story_bible():
    """Test IntakeAgent updates Story Bible with brief."""
    agent = IntakeAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert bible.brief.genre != ""
    assert bible.brief.premise != ""
    assert bible.brief.target_length > 0
    assert bible.brief.tone != ""
    assert bible.brief.audience != ""
    assert bible.brief.pov != ""


def test_intake_agent_records_changes():
    """Test IntakeAgent records changes to Story Bible."""
    agent = IntakeAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.deltas) == 1
    assert bible.deltas[0].agent_name == "Intake Agent"
    assert "book brief" in bible.deltas[0].summary.lower()


def test_intake_agent_increments_version():
    """Test IntakeAgent increments Story Bible version."""
    agent = IntakeAgent()
    bible = StoryBible(project_name="Test")
    initial_version = bible.version
    
    agent.execute(bible)
    
    assert bible.version > initial_version

"""Tests for Character Agent."""

import pytest
from storytelling_workspace.agents.character import CharacterAgent
from storytelling_workspace.story_bible import StoryBible


def test_character_agent_initialization():
    """Test CharacterAgent can be initialized."""
    agent = CharacterAgent()
    
    assert agent.name == "Character Agent"


def test_character_agent_execute():
    """Test CharacterAgent executes and creates characters."""
    agent = CharacterAgent()
    bible = StoryBible(project_name="Test")
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert result["characters_count"] > 0
    assert "characters" in result


def test_character_agent_creates_protagonist():
    """Test CharacterAgent creates protagonist."""
    agent = CharacterAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    # Should have at least one protagonist
    protagonists = [char for char in bible.characters.values() if char.role == "protagonist"]
    assert len(protagonists) > 0
    
    protagonist = protagonists[0]
    assert protagonist.name != ""
    assert len(protagonist.goals) > 0
    assert len(protagonist.flaws) > 0
    assert protagonist.arc != ""
    assert protagonist.voice_signature != ""


def test_character_agent_creates_antagonist():
    """Test CharacterAgent creates antagonist."""
    agent = CharacterAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    # Should have at least one antagonist
    antagonists = [char for char in bible.characters.values() if char.role == "antagonist"]
    assert len(antagonists) > 0
    
    antagonist = antagonists[0]
    assert antagonist.name != ""
    assert len(antagonist.goals) > 0
    assert len(antagonist.flaws) > 0


def test_character_agent_creates_supporting_characters():
    """Test CharacterAgent creates supporting characters."""
    agent = CharacterAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    # Should have at least one supporting character
    supporting = [char for char in bible.characters.values() if char.role == "supporting"]
    assert len(supporting) > 0


def test_character_agent_records_changes():
    """Test CharacterAgent records changes to Story Bible."""
    agent = CharacterAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.deltas) == 1
    assert bible.deltas[0].agent_name == "Character Agent"
    assert "character" in bible.deltas[0].summary.lower()


def test_character_agent_increments_version():
    """Test CharacterAgent increments Story Bible version."""
    agent = CharacterAgent()
    bible = StoryBible(project_name="Test")
    initial_version = bible.version
    
    agent.execute(bible)
    
    assert bible.version > initial_version


def test_character_agent_creates_multiple_characters():
    """Test CharacterAgent creates multiple characters."""
    agent = CharacterAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.characters) >= 3  # At least protagonist, antagonist, supporting

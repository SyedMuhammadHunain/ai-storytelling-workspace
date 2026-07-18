"""Tests for Concept Agent."""

import pytest
from storytelling_workspace.agents.concept import ConceptAgent
from storytelling_workspace.story_bible import StoryBible
from storytelling_workspace.models import BookBrief


def test_concept_agent_initialization():
    """Test ConceptAgent can be initialized."""
    agent = ConceptAgent()
    
    assert agent.name == "Concept Agent"


def test_concept_agent_execute():
    """Test ConceptAgent executes and creates concept."""
    agent = ConceptAgent()
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="Test premise")
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "concept" in result
    assert bible.concept.logline != ""
    assert bible.concept.theme != ""


def test_concept_agent_updates_story_bible():
    """Test ConceptAgent updates Story Bible with concept."""
    agent = ConceptAgent()
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="Test premise")
    
    agent.execute(bible)
    
    assert bible.concept.logline != ""
    assert bible.concept.premise != ""
    assert bible.concept.central_conflict != ""
    assert bible.concept.theme != ""


def test_concept_agent_records_changes():
    """Test ConceptAgent records changes to Story Bible."""
    agent = ConceptAgent()
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="Test premise")
    
    agent.execute(bible)
    
    assert len(bible.deltas) == 1
    assert bible.deltas[0].agent_name == "Concept Agent"
    assert "concept" in bible.deltas[0].summary.lower()


def test_concept_agent_increments_version():
    """Test ConceptAgent increments Story Bible version."""
    agent = ConceptAgent()
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="Test premise")
    initial_version = bible.version
    
    agent.execute(bible)
    
    assert bible.version > initial_version

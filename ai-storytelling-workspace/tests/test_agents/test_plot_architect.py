"""Tests for Plot Architect Agent."""

import pytest
from storytelling_workspace.agents.plot_architect import PlotArchitectAgent
from storytelling_workspace.story_bible import StoryBible


def test_plot_architect_agent_initialization():
    """Test PlotArchitectAgent can be initialized."""
    agent = PlotArchitectAgent()
    
    assert agent.name == "Plot Architect Agent"


def test_plot_architect_agent_execute():
    """Test PlotArchitectAgent executes and creates outline."""
    agent = PlotArchitectAgent()
    bible = StoryBible(project_name="Test")
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert result["chapters_count"] > 0
    assert result["plot_threads_count"] > 0


def test_plot_architect_creates_chapters():
    """Test PlotArchitectAgent creates chapter outline."""
    agent = PlotArchitectAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.chapters) > 0
    
    # Check first chapter has required fields
    chapter = bible.get_chapter(1)
    assert chapter is not None
    assert chapter.title != ""
    assert chapter.pov != ""
    assert chapter.goal != ""
    assert chapter.conflict != ""
    assert chapter.word_count_target > 0
    assert chapter.status == "planned"


def test_plot_architect_creates_plot_threads():
    """Test PlotArchitectAgent creates plot threads."""
    agent = PlotArchitectAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.plot_threads) > 0
    
    # Check plot threads have required fields
    for thread in bible.plot_threads.values():
        assert thread.name != ""
        assert thread.description != ""
        assert thread.status != ""
        assert len(thread.chapters) > 0


def test_plot_architect_records_changes():
    """Test PlotArchitectAgent records changes to Story Bible."""
    agent = PlotArchitectAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.deltas) == 1
    assert bible.deltas[0].agent_name == "Plot Architect Agent"
    assert "outline" in bible.deltas[0].summary.lower()


def test_plot_architect_increments_version():
    """Test PlotArchitectAgent increments Story Bible version."""
    agent = PlotArchitectAgent()
    bible = StoryBible(project_name="Test")
    initial_version = bible.version
    
    agent.execute(bible)
    
    assert bible.version > initial_version


def test_plot_architect_creates_ten_chapters():
    """Test PlotArchitectAgent creates 10 chapters for MVP."""
    agent = PlotArchitectAgent()
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.chapters) == 10
    
    # Verify chapters are numbered 1-10
    for i in range(1, 11):
        assert bible.get_chapter(i) is not None

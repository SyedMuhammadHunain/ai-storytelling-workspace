"""Tests for Chapter Drafting Agent."""

import pytest
from storytelling_workspace.agents.chapter_drafting import ChapterDraftingAgent
from storytelling_workspace.agents.plot_architect import PlotArchitectAgent
from storytelling_workspace.story_bible import StoryBible


def test_chapter_drafting_agent_initialization():
    """Test ChapterDraftingAgent can be initialized."""
    agent = ChapterDraftingAgent(chapter_number=1)
    
    assert agent.name == "Chapter Drafting Agent (Ch. 1)"
    assert agent.chapter_number == 1


def test_chapter_drafting_agent_execute():
    """Test ChapterDraftingAgent executes and drafts chapter."""
    # First create outline
    bible = StoryBible(project_name="Test")
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    # Then draft chapter
    agent = ChapterDraftingAgent(chapter_number=1)
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert result["chapter_number"] == 1
    assert result["word_count"] > 0


def test_chapter_drafting_updates_chapter_content():
    """Test ChapterDraftingAgent updates chapter with content."""
    bible = StoryBible(project_name="Test")
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    agent = ChapterDraftingAgent(chapter_number=1)
    agent.execute(bible)
    
    chapter = bible.get_chapter(1)
    assert chapter.content != ""
    assert chapter.status == "drafted"


def test_chapter_drafting_fails_without_outline():
    """Test ChapterDraftingAgent fails gracefully without outline."""
    bible = StoryBible(project_name="Test")
    
    agent = ChapterDraftingAgent(chapter_number=1)
    result = agent.execute(bible)
    
    assert result["success"] is False
    assert "error" in result


def test_chapter_drafting_records_changes():
    """Test ChapterDraftingAgent records changes to Story Bible."""
    bible = StoryBible(project_name="Test")
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    agent = ChapterDraftingAgent(chapter_number=1)
    agent.execute(bible)
    
    # Should have 2 deltas: plot architect + chapter drafting
    assert len(bible.deltas) == 2
    assert bible.deltas[1].agent_name == "Chapter Drafting Agent (Ch. 1)"


def test_chapter_drafting_multiple_chapters():
    """Test multiple ChapterDraftingAgents can work independently."""
    bible = StoryBible(project_name="Test")
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    # Draft multiple chapters
    agent1 = ChapterDraftingAgent(chapter_number=1)
    agent2 = ChapterDraftingAgent(chapter_number=2)
    agent3 = ChapterDraftingAgent(chapter_number=3)
    
    agent1.execute(bible)
    agent2.execute(bible)
    agent3.execute(bible)
    
    # All chapters should be drafted
    assert bible.get_chapter(1).status == "drafted"
    assert bible.get_chapter(2).status == "drafted"
    assert bible.get_chapter(3).status == "drafted"


def test_chapter_drafting_increments_version():
    """Test ChapterDraftingAgent increments Story Bible version."""
    bible = StoryBible(project_name="Test")
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    initial_version = bible.version
    
    agent = ChapterDraftingAgent(chapter_number=1)
    agent.execute(bible)
    
    assert bible.version > initial_version

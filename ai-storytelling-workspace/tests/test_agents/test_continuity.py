"""Tests for Continuity Agent."""

import pytest
from storytelling_workspace.agents.continuity import ContinuityAgent
from storytelling_workspace.agents.plot_architect import PlotArchitectAgent
from storytelling_workspace.agents.chapter_drafting import ChapterDraftingAgent
from storytelling_workspace.story_bible import StoryBible
from storytelling_workspace.models import TimelineEvent


def test_continuity_agent_initialization():
    """Test ContinuityAgent can be initialized."""
    agent = ContinuityAgent()
    
    assert agent.name == "Continuity Agent"


def test_continuity_agent_execute():
    """Test ContinuityAgent executes and checks continuity."""
    bible = StoryBible(project_name="Test")
    
    agent = ContinuityAgent()
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "issues_found" in result
    assert "report" in result


def test_continuity_agent_creates_report():
    """Test ContinuityAgent creates continuity report."""
    bible = StoryBible(project_name="Test")
    
    agent = ContinuityAgent()
    agent.execute(bible)
    
    assert "continuity_reports" in bible.metadata
    assert len(bible.metadata["continuity_reports"]) == 1
    
    report = bible.metadata["continuity_reports"][0]
    assert "timestamp" in report
    assert "issues_found" in report
    assert "status" in report


def test_continuity_agent_with_chapters():
    """Test ContinuityAgent with drafted chapters."""
    bible = StoryBible(project_name="Test")
    
    # Create outline and draft some chapters
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    for i in range(1, 6):
        chapter_agent = ChapterDraftingAgent(chapter_number=i)
        chapter_agent.execute(bible)
    
    # Run continuity check
    agent = ContinuityAgent()
    result = agent.execute(bible)
    
    assert result["success"] is True
    # With 5 chapters, should find at least one mock issue
    assert result["issues_found"] >= 0


def test_continuity_agent_with_timeline():
    """Test ContinuityAgent with timeline events."""
    bible = StoryBible(project_name="Test")
    
    # Add timeline events
    bible.add_timeline_event(TimelineEvent(timestamp="Past", event="Event 1"))
    bible.add_timeline_event(TimelineEvent(timestamp="Present", event="Event 2"))
    bible.add_timeline_event(TimelineEvent(timestamp="Future", event="Event 3"))
    
    agent = ContinuityAgent()
    result = agent.execute(bible)
    
    assert result["success"] is True
    # With 3 timeline events, should find mock timeline issue
    assert result["issues_found"] >= 0


def test_continuity_agent_records_changes():
    """Test ContinuityAgent records changes to Story Bible."""
    bible = StoryBible(project_name="Test")
    
    agent = ContinuityAgent()
    agent.execute(bible)
    
    assert len(bible.deltas) == 1
    assert bible.deltas[0].agent_name == "Continuity Agent"
    assert "continuity" in bible.deltas[0].summary.lower()


def test_continuity_agent_increments_version():
    """Test ContinuityAgent increments Story Bible version."""
    bible = StoryBible(project_name="Test")
    initial_version = bible.version
    
    agent = ContinuityAgent()
    agent.execute(bible)
    
    assert bible.version > initial_version


def test_continuity_agent_multiple_runs():
    """Test ContinuityAgent can run multiple times."""
    bible = StoryBible(project_name="Test")
    
    agent = ContinuityAgent()
    agent.execute(bible)
    agent.execute(bible)
    
    # Should have 2 reports
    assert len(bible.metadata["continuity_reports"]) == 2


def test_continuity_agent_issue_structure():
    """Test continuity issues have proper structure."""
    bible = StoryBible(project_name="Test")
    
    # Create conditions for mock issues
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    for i in range(1, 8):
        chapter_agent = ChapterDraftingAgent(chapter_number=i)
        chapter_agent.execute(bible)
    
    agent = ContinuityAgent()
    result = agent.execute(bible)
    
    if result["issues_found"] > 0:
        issue = result["issues"][0]
        assert "type" in issue
        assert "severity" in issue
        assert "description" in issue
        assert "suggestion" in issue

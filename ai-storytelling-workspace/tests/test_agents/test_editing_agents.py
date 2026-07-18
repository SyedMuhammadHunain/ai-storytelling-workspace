"""Tests for editing phase agents."""

import pytest
from storytelling_workspace.agents.dialogue_voice import DialogueVoiceAgent
from storytelling_workspace.agents.dev_editor import DevelopmentalEditorAgent
from storytelling_workspace.agents.line_editor import LineEditorAgent
from storytelling_workspace.agents.copy_editor import CopyEditorAgent
from storytelling_workspace.agents.proofreader import ProofreaderAgent
from storytelling_workspace.agents.plot_architect import PlotArchitectAgent
from storytelling_workspace.agents.chapter_drafting import ChapterDraftingAgent
from storytelling_workspace.agents.character import CharacterAgent
from storytelling_workspace.story_bible import StoryBible


# Dialogue/Voice Agent Tests

def test_dialogue_voice_agent_initialization():
    """Test DialogueVoiceAgent can be initialized."""
    agent = DialogueVoiceAgent()
    assert agent.name == "Dialogue/Voice Agent"


def test_dialogue_voice_agent_execute():
    """Test DialogueVoiceAgent executes and checks voice."""
    bible = StoryBible(project_name="Test")
    agent = DialogueVoiceAgent()
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "findings" in result
    assert "report" in result


def test_dialogue_voice_agent_creates_report():
    """Test DialogueVoiceAgent creates voice report."""
    bible = StoryBible(project_name="Test")
    agent = DialogueVoiceAgent()
    agent.execute(bible)
    
    assert "voice_reports" in bible.metadata
    assert len(bible.metadata["voice_reports"]) == 1


# Developmental Editor Agent Tests

def test_dev_editor_agent_initialization():
    """Test DevelopmentalEditorAgent can be initialized."""
    agent = DevelopmentalEditorAgent()
    assert agent.name == "Developmental Editor Agent"


def test_dev_editor_agent_execute():
    """Test DevelopmentalEditorAgent executes and generates notes."""
    bible = StoryBible(project_name="Test")
    agent = DevelopmentalEditorAgent()
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "notes" in result
    assert len(result["notes"]) > 0


def test_dev_editor_agent_creates_report():
    """Test DevelopmentalEditorAgent creates dev edit report."""
    bible = StoryBible(project_name="Test")
    agent = DevelopmentalEditorAgent()
    agent.execute(bible)
    
    assert "dev_edit_reports" in bible.metadata
    assert len(bible.metadata["dev_edit_reports"]) == 1
    assert "overall_assessment" in bible.metadata["dev_edit_reports"][0]


def test_dev_editor_notes_structure():
    """Test developmental notes have proper structure."""
    bible = StoryBible(project_name="Test")
    agent = DevelopmentalEditorAgent()
    result = agent.execute(bible)
    
    for note in result["notes"]:
        assert "category" in note
        assert "priority" in note
        assert "description" in note
        assert "suggestion" in note


# Line Editor Agent Tests

def test_line_editor_agent_initialization():
    """Test LineEditorAgent can be initialized."""
    agent = LineEditorAgent()
    assert agent.name == "Line Editor Agent"


def test_line_editor_agent_execute():
    """Test LineEditorAgent executes and generates suggestions."""
    bible = StoryBible(project_name="Test")
    agent = LineEditorAgent()
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "suggestions" in result


def test_line_editor_agent_creates_report():
    """Test LineEditorAgent creates line edit report."""
    bible = StoryBible(project_name="Test")
    agent = LineEditorAgent()
    agent.execute(bible)
    
    assert "line_edit_reports" in bible.metadata
    assert len(bible.metadata["line_edit_reports"]) == 1


# Copy Editor Agent Tests

def test_copy_editor_agent_initialization():
    """Test CopyEditorAgent can be initialized."""
    agent = CopyEditorAgent()
    assert agent.name == "Copy Editor Agent"


def test_copy_editor_agent_execute():
    """Test CopyEditorAgent executes and generates corrections."""
    bible = StoryBible(project_name="Test")
    agent = CopyEditorAgent()
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "corrections" in result


def test_copy_editor_agent_creates_report():
    """Test CopyEditorAgent creates copy edit report."""
    bible = StoryBible(project_name="Test")
    agent = CopyEditorAgent()
    agent.execute(bible)
    
    assert "copy_edit_reports" in bible.metadata
    assert len(bible.metadata["copy_edit_reports"]) == 1


def test_copy_editor_corrections_structure():
    """Test copy edit corrections have proper structure."""
    bible = StoryBible(project_name="Test")
    # Add chapters so corrections are generated
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    agent = CopyEditorAgent()
    result = agent.execute(bible)
    
    if len(result["corrections"]) > 0:
        correction = result["corrections"][0]
        assert "type" in correction
        assert "description" in correction
        assert "correction" in correction


# Proofreader Agent Tests

def test_proofreader_agent_initialization():
    """Test ProofreaderAgent can be initialized."""
    agent = ProofreaderAgent()
    assert agent.name == "Proofreader Agent"


def test_proofreader_agent_execute():
    """Test ProofreaderAgent executes and finds issues."""
    bible = StoryBible(project_name="Test")
    agent = ProofreaderAgent()
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "issues" in result
    assert "report" in result


def test_proofreader_agent_creates_report():
    """Test ProofreaderAgent creates proofread report."""
    bible = StoryBible(project_name="Test")
    agent = ProofreaderAgent()
    agent.execute(bible)
    
    assert "proofread_reports" in bible.metadata
    assert len(bible.metadata["proofread_reports"]) == 1


def test_proofreader_issues_structure():
    """Test proofreading issues have proper structure."""
    bible = StoryBible(project_name="Test")
    # Add chapters so issues are generated
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    agent = ProofreaderAgent()
    result = agent.execute(bible)
    
    if len(result["issues"]) > 0:
        issue = result["issues"][0]
        assert "type" in issue
        assert "description" in issue
        assert "severity" in issue


# Integration Tests

def test_all_editing_agents_record_changes():
    """Test all editing agents record changes to Story Bible."""
    bible = StoryBible(project_name="Test")
    
    agents = [
        DialogueVoiceAgent(),
        DevelopmentalEditorAgent(),
        LineEditorAgent(),
        CopyEditorAgent(),
        ProofreaderAgent()
    ]
    
    for agent in agents:
        agent.execute(bible)
    
    assert len(bible.deltas) == 5


def test_editing_agents_increment_version():
    """Test editing agents increment Story Bible version."""
    bible = StoryBible(project_name="Test")
    initial_version = bible.version
    
    agent = DevelopmentalEditorAgent()
    agent.execute(bible)
    
    assert bible.version > initial_version

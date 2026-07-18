"""Tests for workflow orchestrator."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from io import StringIO

from storytelling_workspace.orchestrator import WorkflowOrchestrator
from storytelling_workspace.story_bible import StoryBible


def test_orchestrator_initialization():
    """Test WorkflowOrchestrator can be initialized."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    assert orchestrator.project_name == "Test Book"
    assert orchestrator.output_dir == "output"
    assert isinstance(orchestrator.bible, StoryBible)


def test_orchestrator_custom_output_dir():
    """Test WorkflowOrchestrator with custom output directory."""
    orchestrator = WorkflowOrchestrator(
        project_name="Test Book",
        output_dir="custom_output"
    )
    
    assert orchestrator.output_dir == "custom_output"


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_execute_full_workflow(mock_input):
    """Test WorkflowOrchestrator executes full workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = WorkflowOrchestrator(
            project_name="Test Book",
            output_dir=tmpdir
        )
        
        result = orchestrator.execute()
        
        assert result is True
        
        # Verify Story Bible was updated
        bible = orchestrator.get_story_bible()
        assert bible.brief is not None
        assert bible.concept is not None
        assert len(bible.characters) > 0
        assert len(bible.chapters) > 0


@patch('builtins.input', return_value='3')  # Abort at first checkpoint
def test_orchestrator_abort_at_checkpoint_1(mock_input):
    """Test WorkflowOrchestrator handles abort at checkpoint 1."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    result = orchestrator.execute()
    
    assert result is False


@patch('builtins.input', side_effect=['1', '3'])  # Approve first, abort second
def test_orchestrator_abort_at_checkpoint_2(mock_input):
    """Test WorkflowOrchestrator handles abort at checkpoint 2."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    result = orchestrator.execute()
    
    assert result is False


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_creates_all_agents(mock_input):
    """Test WorkflowOrchestrator runs all 15 agents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = WorkflowOrchestrator(
            project_name="Test Book",
            output_dir=tmpdir
        )
        
        orchestrator.execute()
        
        bible = orchestrator.get_story_bible()
        
        # Verify all phases completed
        assert bible.brief is not None  # Intake
        assert bible.concept is not None  # Concept
        assert len(bible.characters) > 0  # Character
        assert len(bible.chapters) > 0  # Plot Architect + Chapter Drafting
        assert "continuity_reports" in bible.metadata  # Continuity
        assert "voice_reports" in bible.metadata  # Dialogue/Voice
        assert "dev_edit_reports" in bible.metadata  # Dev Editor
        assert "line_edit_reports" in bible.metadata  # Line Editor
        assert "copy_edit_reports" in bible.metadata  # Copy Editor
        assert "proofread_reports" in bible.metadata  # Proofreader
        assert "front_matter" in bible.metadata  # Front Matter
        assert "back_matter" in bible.metadata  # Back Matter
        assert "compiled_manuscript" in bible.metadata  # Compilation
        assert "qa_reports" in bible.metadata  # QA


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_drafts_all_chapters(mock_input):
    """Test WorkflowOrchestrator drafts all 10 chapters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = WorkflowOrchestrator(
            project_name="Test Book",
            output_dir=tmpdir
        )
        
        orchestrator.execute()
        
        bible = orchestrator.get_story_bible()
        
        # Should have 10 chapters
        assert len(bible.chapters) == 10
        
        # All chapters should be drafted
        for i in range(1, 11):
            chapter = bible.get_chapter(i)
            assert chapter is not None
            assert chapter.status == "drafted"
            assert chapter.content != ""


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_exports_files(mock_input):
    """Test WorkflowOrchestrator exports manuscript and Story Bible."""
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = WorkflowOrchestrator(
            project_name="Test Book",
            output_dir=tmpdir
        )
        
        orchestrator.execute()
        
        # Verify files were created
        manuscript_path = os.path.join(tmpdir, "manuscript.txt")
        story_bible_path = os.path.join(tmpdir, "story_bible.json")
        
        assert os.path.exists(manuscript_path)
        assert os.path.exists(story_bible_path)
        
        # Verify manuscript has content
        with open(manuscript_path, "r") as f:
            content = f.read()
        assert len(content) > 0


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_story_bible_versioning(mock_input):
    """Test WorkflowOrchestrator increments Story Bible version."""
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = WorkflowOrchestrator(
            project_name="Test Book",
            output_dir=tmpdir
        )
        
        initial_version = orchestrator.bible.version
        
        orchestrator.execute()
        
        # Version should have incremented significantly (15+ agents)
        assert orchestrator.bible.version > initial_version + 15


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_get_story_bible(mock_input):
    """Test WorkflowOrchestrator get_story_bible method."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    bible = orchestrator.get_story_bible()
    
    assert isinstance(bible, StoryBible)
    assert bible.project_name == "Test Book"


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_phase_1_setup(mock_input):
    """Test WorkflowOrchestrator Phase 1 completes successfully."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    result = orchestrator._phase_1_setup()
    
    assert result is True
    assert orchestrator.bible.brief is not None
    assert orchestrator.bible.concept is not None
    assert len(orchestrator.bible.characters) > 0


@patch('builtins.input', side_effect=['1', '1', '1', '1'])
def test_orchestrator_phase_2_drafting(mock_input):
    """Test WorkflowOrchestrator Phase 2 completes successfully."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    # Run phase 1 first
    orchestrator._phase_1_setup()
    
    # Run phase 2
    result = orchestrator._phase_2_drafting()
    
    assert result is True
    assert len(orchestrator.bible.chapters) == 10


def test_orchestrator_phase_3_editing():
    """Test WorkflowOrchestrator Phase 3 completes successfully."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    # Setup some data
    orchestrator.bible.brief.genre = "Fantasy"
    
    with patch('builtins.input', return_value='1'):
        result = orchestrator._phase_3_editing()
    
    assert result is True
    assert "dev_edit_reports" in orchestrator.bible.metadata


@patch('builtins.input', return_value='1')
def test_orchestrator_phase_4_assembly(mock_input):
    """Test WorkflowOrchestrator Phase 4 completes successfully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = WorkflowOrchestrator(
            project_name="Test Book",
            output_dir=tmpdir
        )
        
        # Setup minimal data
        orchestrator.bible.brief.genre = "Fantasy"
        
        result = orchestrator._phase_4_assembly()
        
        assert result is True
        assert "front_matter" in orchestrator.bible.metadata
        assert "back_matter" in orchestrator.bible.metadata




@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_handles_agent_exception_in_phase_1(mock_input):
    """Test WorkflowOrchestrator handles agent exception in Phase 1."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    # Mock an agent to raise an exception
    with patch('storytelling_workspace.agents.intake.IntakeAgent.execute', side_effect=Exception("Agent failure")):
        result = orchestrator.execute()
        
        # Should return False due to exception
        assert result is False


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_handles_agent_exception_in_phase_2(mock_input):
    """Test WorkflowOrchestrator handles agent exception in Phase 2."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    # Mock plot architect to raise an exception
    with patch('storytelling_workspace.agents.plot_architect.PlotArchitectAgent.execute', side_effect=Exception("Plot failure")):
        result = orchestrator.execute()
        
        # Should return False due to exception
        assert result is False


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_handles_agent_exception_in_phase_3(mock_input):
    """Test WorkflowOrchestrator handles agent exception in Phase 3."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    # Mock dialogue/voice agent to raise an exception
    with patch('storytelling_workspace.agents.dialogue_voice.DialogueVoiceAgent.execute', side_effect=Exception("Editing failure")):
        result = orchestrator.execute()
        
        # Should return False due to exception
        assert result is False


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_handles_agent_exception_in_phase_4(mock_input):
    """Test WorkflowOrchestrator handles agent exception in Phase 4."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    # Mock front matter agent to raise an exception
    with patch('storytelling_workspace.agents.front_matter.FrontMatterAgent.execute', side_effect=Exception("Assembly failure")):
        result = orchestrator.execute()
        
        # Should return False due to exception
        assert result is False


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_handles_checkpoint_exception(mock_input):
    """Test WorkflowOrchestrator handles checkpoint exception."""
    orchestrator = WorkflowOrchestrator(project_name="Test Book")
    
    # Mock checkpoint to raise an exception
    with patch('storytelling_workspace.checkpoint.Checkpoint.execute', side_effect=Exception("Checkpoint failure")):
        result = orchestrator.execute()
        
        # Should return False due to exception
        assert result is False


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_orchestrator_handles_export_failure(mock_input):
    """Test WorkflowOrchestrator handles export directory creation failure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a file where the output directory should be
        output_path = os.path.join(tmpdir, "output")
        with open(output_path, "w") as f:
            f.write("blocking file")
        
        orchestrator = WorkflowOrchestrator(
            project_name="Test Book",
            output_dir=output_path
        )
        
        # Mock the export agent to raise an exception when trying to create directory
        with patch('storytelling_workspace.agents.export.ExportAgent.execute', side_effect=Exception("Cannot create directory")):
            result = orchestrator.execute()
            
            # Should return False due to exception
            assert result is False

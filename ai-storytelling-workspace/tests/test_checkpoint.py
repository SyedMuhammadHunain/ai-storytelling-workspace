"""Tests for human checkpoint system."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

from storytelling_workspace.checkpoint import (
    Checkpoint, CheckpointDecision, CheckpointManager
)
from storytelling_workspace.story_bible import StoryBible
from storytelling_workspace.models import Character


def test_checkpoint_initialization():
    """Test Checkpoint can be initialized."""
    checkpoint = Checkpoint(
        name="Test Checkpoint",
        description="Test description"
    )
    
    assert checkpoint.name == "Test Checkpoint"
    assert checkpoint.description == "Test description"


@patch('builtins.input', return_value='1')
@patch('sys.stdout', new_callable=StringIO)
def test_checkpoint_approve(mock_stdout, mock_input):
    """Test checkpoint with approve decision."""
    checkpoint = Checkpoint("Test", "Test checkpoint")
    bible = StoryBible(project_name="Test")
    
    decision = checkpoint.execute(bible)
    
    assert decision == CheckpointDecision.APPROVE


@patch('builtins.input', return_value='3')
@patch('sys.stdout', new_callable=StringIO)
def test_checkpoint_abort(mock_stdout, mock_input):
    """Test checkpoint with abort decision."""
    checkpoint = Checkpoint("Test", "Test checkpoint")
    bible = StoryBible(project_name="Test")
    
    decision = checkpoint.execute(bible)
    
    assert decision == CheckpointDecision.ABORT


@patch('builtins.input', side_effect=['2', '1'])  # Try edit, then approve
@patch('sys.stdout', new_callable=StringIO)
def test_checkpoint_edit_not_implemented(mock_stdout, mock_input):
    """Test checkpoint handles edit option (not implemented in MVP)."""
    checkpoint = Checkpoint("Test", "Test checkpoint")
    bible = StoryBible(project_name="Test")
    
    decision = checkpoint.execute(bible)
    
    # Should eventually approve after edit attempt
    assert decision == CheckpointDecision.APPROVE


@patch('builtins.input', side_effect=['invalid', '99', '1'])
@patch('sys.stdout', new_callable=StringIO)
def test_checkpoint_invalid_input(mock_stdout, mock_input):
    """Test checkpoint handles invalid input gracefully."""
    checkpoint = Checkpoint("Test", "Test checkpoint")
    bible = StoryBible(project_name="Test")
    
    decision = checkpoint.execute(bible)
    
    # Should eventually get valid input
    assert decision == CheckpointDecision.APPROVE


@patch('builtins.input', side_effect=KeyboardInterrupt())
@patch('sys.stdout', new_callable=StringIO)
def test_checkpoint_keyboard_interrupt(mock_stdout, mock_input):
    """Test checkpoint handles keyboard interrupt."""
    checkpoint = Checkpoint("Test", "Test checkpoint")
    bible = StoryBible(project_name="Test")
    
    decision = checkpoint.execute(bible)
    
    assert decision == CheckpointDecision.ABORT


@patch('builtins.input', return_value='1')
@patch('sys.stdout', new_callable=StringIO)
def test_checkpoint_displays_story_bible(mock_stdout, mock_input):
    """Test checkpoint displays Story Bible summary."""
    checkpoint = Checkpoint("Test", "Test checkpoint")
    bible = StoryBible(project_name="Test Project")
    bible.add_character(Character(name="Alice", role="protagonist"))
    
    checkpoint.execute(bible)
    
    output = mock_stdout.getvalue()
    assert "CHECKPOINT: Test" in output
    assert "Test Project" in output
    assert "Characters: 1" in output


def test_checkpoint_manager_checkpoint_1():
    """Test CheckpointManager creates checkpoint 1."""
    checkpoint = CheckpointManager.create_checkpoint_1()
    
    assert checkpoint.name == "Checkpoint 1: Book Brief"
    assert "brief" in checkpoint.description.lower()


def test_checkpoint_manager_checkpoint_2():
    """Test CheckpointManager creates checkpoint 2."""
    checkpoint = CheckpointManager.create_checkpoint_2()
    
    assert checkpoint.name == "Checkpoint 2: Concept"
    assert "concept" in checkpoint.description.lower()


def test_checkpoint_manager_checkpoint_3():
    """Test CheckpointManager creates checkpoint 3."""
    checkpoint = CheckpointManager.create_checkpoint_3()
    
    assert checkpoint.name == "Checkpoint 3: Story Bible v1"
    assert "world" in checkpoint.description.lower() or "character" in checkpoint.description.lower()


def test_checkpoint_manager_checkpoint_4():
    """Test CheckpointManager creates checkpoint 4."""
    checkpoint = CheckpointManager.create_checkpoint_4()
    
    assert checkpoint.name == "Checkpoint 4: Plot Outline"
    assert "outline" in checkpoint.description.lower()
    assert "important" in checkpoint.description.lower()


def test_checkpoint_manager_checkpoint_5():
    """Test CheckpointManager creates checkpoint 5."""
    checkpoint = CheckpointManager.create_checkpoint_5()
    
    assert checkpoint.name == "Checkpoint 5: Developmental Notes"
    assert "developmental" in checkpoint.description.lower()


def test_checkpoint_manager_checkpoint_6():
    """Test CheckpointManager creates checkpoint 6."""
    checkpoint = CheckpointManager.create_checkpoint_6()
    
    assert checkpoint.name == "Checkpoint 6: Final Sign-off"
    assert "final" in checkpoint.description.lower()


def test_checkpoint_decision_enum():
    """Test CheckpointDecision enum values."""
    assert CheckpointDecision.APPROVE.value == "approve"
    assert CheckpointDecision.EDIT.value == "edit"
    assert CheckpointDecision.ABORT.value == "abort"

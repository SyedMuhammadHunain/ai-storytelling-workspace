"""
Unit tests for Checkpoint model.
"""

import pytest
from datetime import datetime

from storytelling_workspace.db.models import Checkpoint, CheckpointStatus, CheckpointType


def test_checkpoint_creation():
    """Test creating a Checkpoint instance."""
    checkpoint = Checkpoint(
        project_id="test-project-id",
        story_bible_id="test-bible-id",
        checkpoint_type=CheckpointType.CONCEPT,
        phase="concept_development",
        agent_name="ConceptAgent",
        content={"test": "data"},
    )
    
    assert checkpoint.project_id == "test-project-id"
    assert checkpoint.story_bible_id == "test-bible-id"
    assert checkpoint.checkpoint_type == CheckpointType.CONCEPT
    assert checkpoint.phase == "concept_development"
    assert checkpoint.agent_name == "ConceptAgent"
    assert checkpoint.status == CheckpointStatus.PENDING


def test_checkpoint_approve():
    """Test approving a checkpoint."""
    checkpoint = Checkpoint(
        project_id="test-id",
        story_bible_id="test-id",
        checkpoint_type=CheckpointType.CHAPTER,
        phase="drafting",
        agent_name="ChapterAgent",
        content={},
    )
    
    checkpoint.approve("Looks good!")
    
    assert checkpoint.status == CheckpointStatus.APPROVED
    assert checkpoint.user_feedback == "Looks good!"
    assert isinstance(checkpoint.reviewed_at, datetime)


def test_checkpoint_reject():
    """Test rejecting a checkpoint."""
    checkpoint = Checkpoint(
        project_id="test-id",
        story_bible_id="test-id",
        checkpoint_type=CheckpointType.OUTLINE,
        phase="planning",
        agent_name="PlotAgent",
        content={},
    )
    
    checkpoint.reject("Needs more detail")
    
    assert checkpoint.status == CheckpointStatus.REJECTED
    assert checkpoint.rejection_reason == "Needs more detail"
    assert isinstance(checkpoint.reviewed_at, datetime)


def test_checkpoint_skip():
    """Test skipping a checkpoint."""
    checkpoint = Checkpoint(
        project_id="test-id",
        story_bible_id="test-id",
        checkpoint_type=CheckpointType.FINAL,
        phase="review",
        agent_name="QAAgent",
        content={},
    )
    
    checkpoint.skip()
    
    assert checkpoint.status == CheckpointStatus.SKIPPED
    assert isinstance(checkpoint.reviewed_at, datetime)


def test_checkpoint_status_properties():
    """Test checkpoint status properties."""
    checkpoint = Checkpoint(
        project_id="test-id",
        story_bible_id="test-id",
        checkpoint_type=CheckpointType.CHARACTERS,
        phase="character_dev",
        agent_name="CharacterAgent",
        content={},
    )
    
    assert checkpoint.is_pending
    assert not checkpoint.is_approved
    assert not checkpoint.is_rejected
    
    checkpoint.approve()
    
    assert not checkpoint.is_pending
    assert checkpoint.is_approved
    assert not checkpoint.is_rejected

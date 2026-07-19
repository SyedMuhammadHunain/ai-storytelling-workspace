"""
Unit tests for WorkflowState model.
"""

import pytest
from datetime import datetime
from decimal import Decimal

from storytelling_workspace.db.models import WorkflowState, WorkflowStatus


def test_workflow_state_creation():
    """Test creating a WorkflowState instance."""
    workflow = WorkflowState(
        project_id="test-project-id",
        current_phase="concept_development",
        current_agent="ConceptAgent",
        total_steps=10,
    )
    
    assert workflow.project_id == "test-project-id"
    assert workflow.current_phase == "concept_development"
    assert workflow.current_agent == "ConceptAgent"
    assert workflow.total_steps == 10
    assert workflow.completed_steps == 0
    assert workflow.status == WorkflowStatus.RUNNING


def test_workflow_update_progress():
    """Test updating workflow progress."""
    workflow = WorkflowState(
        project_id="test-id",
        current_phase="drafting",
        total_steps=10,
    )
    
    workflow.update_progress(5)
    
    assert workflow.completed_steps == 5
    assert workflow.progress_percentage == Decimal("50.00")


def test_workflow_pause():
    """Test pausing workflow."""
    workflow = WorkflowState(
        project_id="test-id",
        current_phase="editing",
        total_steps=5,
    )
    
    workflow.pause()
    
    assert workflow.status == WorkflowStatus.PAUSED
    assert isinstance(workflow.paused_at, datetime)


def test_workflow_resume():
    """Test resuming workflow."""
    workflow = WorkflowState(
        project_id="test-id",
        current_phase="editing",
        total_steps=5,
    )
    
    workflow.pause()
    workflow.resume()
    
    assert workflow.status == WorkflowStatus.RUNNING
    assert isinstance(workflow.resumed_at, datetime)


def test_workflow_complete():
    """Test completing workflow."""
    workflow = WorkflowState(
        project_id="test-id",
        current_phase="final",
        total_steps=10,
    )
    
    workflow.complete()
    
    assert workflow.status == WorkflowStatus.COMPLETED
    assert workflow.progress_percentage == Decimal("100.00")
    assert isinstance(workflow.completed_at, datetime)


def test_workflow_fail():
    """Test failing workflow."""
    workflow = WorkflowState(
        project_id="test-id",
        current_phase="drafting",
        total_steps=10,
    )
    
    workflow.fail("Test error", "Stack trace here")
    
    assert workflow.status == WorkflowStatus.FAILED
    assert workflow.error_message == "Test error"
    assert workflow.error_stack == "Stack trace here"
    assert isinstance(workflow.completed_at, datetime)


def test_workflow_cancel():
    """Test cancelling workflow."""
    workflow = WorkflowState(
        project_id="test-id",
        current_phase="drafting",
        total_steps=10,
    )
    
    workflow.cancel()
    
    assert workflow.status == WorkflowStatus.CANCELLED
    assert isinstance(workflow.completed_at, datetime)


def test_workflow_status_properties():
    """Test workflow status properties."""
    workflow = WorkflowState(
        project_id="test-id",
        current_phase="test",
        total_steps=5,
    )
    
    assert workflow.is_running
    assert not workflow.is_paused
    assert not workflow.is_completed
    assert not workflow.is_failed
    
    workflow.pause()
    assert workflow.is_paused
    
    workflow.complete()
    assert workflow.is_completed

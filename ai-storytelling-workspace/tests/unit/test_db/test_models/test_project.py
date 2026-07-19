"""
Unit tests for Project model.
"""

import pytest
from datetime import datetime

from storytelling_workspace.db.models import Project, ProjectStatus


def test_project_creation():
    """Test creating a Project instance."""
    project = Project(
        name="Test Novel",
        description="A test novel project",
        genre="Fantasy",
        target_length=80000,
    )
    
    assert project.name == "Test Novel"
    assert project.description == "A test novel project"
    assert project.genre == "Fantasy"
    assert project.target_length == 80000
    assert project.status == ProjectStatus.DRAFT
    assert project.deleted_at is None


def test_project_status_enum():
    """Test ProjectStatus enum values."""
    assert ProjectStatus.DRAFT == "draft"
    assert ProjectStatus.IN_PROGRESS == "in_progress"
    assert ProjectStatus.PAUSED == "paused"
    assert ProjectStatus.COMPLETED == "completed"
    assert ProjectStatus.ARCHIVED == "archived"


def test_project_soft_delete():
    """Test soft delete functionality."""
    project = Project(name="Test Project")
    
    assert not project.is_deleted
    assert project.deleted_at is None
    
    project.soft_delete()
    
    assert project.is_deleted
    assert isinstance(project.deleted_at, datetime)


def test_project_restore():
    """Test restoring a soft deleted project."""
    project = Project(name="Test Project")
    project.soft_delete()
    
    assert project.is_deleted
    
    project.restore()
    
    assert not project.is_deleted
    assert project.deleted_at is None


def test_project_repr():
    """Test string representation."""
    project = Project(name="Test Novel", status=ProjectStatus.IN_PROGRESS)
    repr_str = repr(project)
    
    assert "Project" in repr_str
    assert "Test Novel" in repr_str
    assert "in_progress" in repr_str


def test_project_to_dict():
    """Test converting project to dictionary."""
    project = Project(
        name="Test Novel",
        description="Test description",
        genre="Sci-Fi",
    )
    
    project_dict = project.to_dict()
    
    assert isinstance(project_dict, dict)
    assert project_dict["name"] == "Test Novel"
    assert project_dict["description"] == "Test description"
    assert project_dict["genre"] == "Sci-Fi"

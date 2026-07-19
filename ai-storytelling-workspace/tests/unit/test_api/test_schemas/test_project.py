"""Unit tests for project schemas."""

import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime

from storytelling_workspace.api.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatsResponse,
)


class TestProjectCreate:
    """Tests for ProjectCreate schema."""
    
    def test_valid_project_create(self):
        """Test creating project with valid data."""
        data = {
            "name": "My Novel",
            "description": "A great story",
            "genre": "Fantasy",
            "target_length": 80000
        }
        project = ProjectCreate(**data)
        
        assert project.name == "My Novel"
        assert project.description == "A great story"
        assert project.genre == "Fantasy"
        assert project.target_length == 80000
    
    def test_project_create_minimal(self):
        """Test creating project with minimal required fields."""
        project = ProjectCreate(name="Test Novel")
        
        assert project.name == "Test Novel"
        assert project.description is None
        assert project.genre is None
        assert project.target_length == 80000  # Default value
    
    def test_project_create_strips_whitespace(self):
        """Test that name whitespace is stripped."""
        project = ProjectCreate(name="  My Novel  ")
        assert project.name == "My Novel"
    
    def test_project_create_empty_name_fails(self):
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(name="")
        
        errors = exc_info.value.errors()
        # Check that validation error occurred (either min_length or custom validator)
        assert len(errors) > 0
        assert errors[0]['loc'] == ('name',)
    
    def test_project_create_whitespace_only_name_fails(self):
        """Test that whitespace-only name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(name="   ")
        
        errors = exc_info.value.errors()
        assert any("Name cannot be empty" in str(e) for e in errors)
    
    def test_project_create_target_length_too_small(self):
        """Test that target length below minimum fails."""
        with pytest.raises(ValidationError):
            ProjectCreate(name="Test", target_length=5000)
    
    def test_project_create_target_length_too_large(self):
        """Test that target length above maximum fails."""
        with pytest.raises(ValidationError):
            ProjectCreate(name="Test", target_length=300000)
    
    def test_project_create_name_too_long(self):
        """Test that name exceeding max length fails."""
        with pytest.raises(ValidationError):
            ProjectCreate(name="A" * 256)


class TestProjectUpdate:
    """Tests for ProjectUpdate schema."""
    
    def test_valid_project_update(self):
        """Test updating project with valid data."""
        data = {
            "name": "Updated Novel",
            "status": "in_progress"
        }
        update = ProjectUpdate(**data)
        
        assert update.name == "Updated Novel"
        assert update.status == "in_progress"
        assert update.description is None  # Not provided
    
    def test_project_update_all_fields_optional(self):
        """Test that all fields are optional."""
        update = ProjectUpdate()
        
        assert update.name is None
        assert update.description is None
        assert update.genre is None
        assert update.target_length is None
        assert update.status is None
    
    def test_project_update_invalid_status(self):
        """Test that invalid status raises validation error."""
        with pytest.raises(ValidationError):
            ProjectUpdate(status="invalid_status")
    
    def test_project_update_valid_statuses(self):
        """Test all valid status values."""
        valid_statuses = ['draft', 'in_progress', 'paused', 'completed', 'archived']
        
        for status in valid_statuses:
            update = ProjectUpdate(status=status)
            assert update.status == status


class TestProjectResponse:
    """Tests for ProjectResponse schema."""
    
    def test_project_response_from_dict(self):
        """Test creating response from dictionary."""
        data = {
            "id": uuid4(),
            "name": "Test Novel",
            "description": "A test",
            "genre": "Fantasy",
            "target_length": 80000,
            "status": "draft",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        response = ProjectResponse(**data)
        
        assert response.name == "Test Novel"
        assert response.genre == "Fantasy"
        assert response.status == "draft"


class TestProjectListResponse:
    """Tests for ProjectListResponse schema."""
    
    def test_project_list_response(self):
        """Test creating list response."""
        project_data = {
            "id": uuid4(),
            "name": "Test Novel",
            "description": None,
            "genre": "Fantasy",
            "target_length": 80000,
            "status": "draft",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        data = {
            "projects": [ProjectResponse(**project_data)],
            "total": 1,
            "page": 1,
            "page_size": 20
        }
        response = ProjectListResponse(**data)
        
        assert len(response.projects) == 1
        assert response.total == 1
        assert response.page == 1
        assert response.page_size == 20
    
    def test_project_list_response_empty(self):
        """Test creating empty list response."""
        data = {
            "projects": [],
            "total": 0,
            "page": 1,
            "page_size": 20
        }
        response = ProjectListResponse(**data)
        
        assert len(response.projects) == 0
        assert response.total == 0


class TestProjectStatsResponse:
    """Tests for ProjectStatsResponse schema."""
    
    def test_project_stats_response(self):
        """Test creating stats response."""
        data = {
            "project_id": uuid4(),
            "status": "in_progress",
            "word_count": 45000,
            "chapter_count": 15,
            "image_count": 8,
            "checkpoint_count": 3,
            "bible_version": 2
        }
        response = ProjectStatsResponse(**data)
        
        assert response.word_count == 45000
        assert response.chapter_count == 15
        assert response.image_count == 8
    
    def test_project_stats_response_defaults(self):
        """Test stats response with default values."""
        data = {
            "project_id": uuid4(),
            "status": "draft"
        }
        response = ProjectStatsResponse(**data)
        
        assert response.word_count == 0
        assert response.chapter_count == 0
        assert response.image_count == 0
        assert response.checkpoint_count == 0
        assert response.bible_version == 0

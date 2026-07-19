"""
Unit tests for repository layer.

Tests CRUD operations and custom queries for all repositories.
"""

import pytest
import pytest_asyncio
from datetime import datetime
from uuid import uuid4

from storytelling_workspace.db.models.project import Project, ProjectStatus
from storytelling_workspace.db.models.story_bible import StoryBible
from storytelling_workspace.db.models.checkpoint import Checkpoint, CheckpointStatus, CheckpointType
from storytelling_workspace.db.models.image import Image, ImageType
from storytelling_workspace.db.models.workflow_state import WorkflowState, WorkflowStatus
from storytelling_workspace.db.repositories import (
    ProjectRepository,
    StoryBibleRepository,
    CheckpointRepository,
    ImageRepository,
    WorkflowStateRepository,
)


class TestProjectRepository:
    """Test ProjectRepository operations."""
    
    @pytest_asyncio.fixture
    async def repo(self, async_session):
        """Create ProjectRepository instance."""
        return ProjectRepository(async_session)
    
    @pytest_asyncio.fixture
    async def sample_project(self, repo):
        """Create a sample project."""
        return await repo.create(
            name="Test Novel",
            genre="Fantasy",
            target_length=80000,
            status=ProjectStatus.IN_PROGRESS
        )
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_create_project(self, repo):
        """Test creating a project."""
        project = await repo.create(
            name="My Novel",
            genre="Science Fiction",
            target_length=100000
        )
        
        assert project.id is not None
        assert project.name == "My Novel"
        assert project.genre == "Science Fiction"
        assert project.status == ProjectStatus.DRAFT
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, sample_project):
        """Test getting project by ID."""
        project = await repo.get_by_id(sample_project.id)
        
        assert project is not None
        assert project.id == sample_project.id
        assert project.name == sample_project.name
    
    @pytest.mark.asyncio
    async def test_get_by_status(self, repo, sample_project):
        """Test getting projects by status."""
        projects = await repo.get_by_status(ProjectStatus.IN_PROGRESS)
        
        assert len(projects) > 0
        assert all(p.status == ProjectStatus.IN_PROGRESS for p in projects)
    
    @pytest.mark.asyncio
    async def test_get_active_projects(self, repo, sample_project):
        """Test getting active projects."""
        projects = await repo.get_active_projects()
        
        assert len(projects) > 0
        assert sample_project.id in [p.id for p in projects]
    
    @pytest.mark.asyncio
    async def test_soft_delete(self, repo, sample_project):
        """Test soft deleting a project."""
        success = await repo.soft_delete(sample_project.id)
        
        assert success is True
        
        # Verify project is soft deleted
        project = await repo.get_by_id(sample_project.id)
        assert project.deleted_at is not None
    
    @pytest.mark.asyncio
    async def test_restore(self, repo, sample_project):
        """Test restoring a soft-deleted project."""
        await repo.soft_delete(sample_project.id)
        restored = await repo.restore(sample_project.id)
        
        assert restored is not None
        assert restored.deleted_at is None
    
    @pytest.mark.asyncio
    async def test_update_status(self, repo, sample_project):
        """Test updating project status."""
        updated = await repo.update_status(sample_project.id, ProjectStatus.COMPLETED)
        
        assert updated is not None
        assert updated.status == ProjectStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_search_by_name(self, repo, sample_project):
        """Test searching projects by name."""
        projects = await repo.search_by_name("Test")
        
        assert len(projects) > 0
        assert any("Test" in p.name for p in projects)
    
    @pytest.mark.asyncio
    async def test_get_by_genre(self, repo, sample_project):
        """Test getting projects by genre."""
        projects = await repo.get_by_genre("Fantasy")
        
        assert len(projects) > 0
        assert all(p.genre == "Fantasy" for p in projects)


class TestStoryBibleRepository:
    """Test StoryBibleRepository operations."""
    
    @pytest_asyncio.fixture
    async def project_repo(self, async_session):
        """Create ProjectRepository instance."""
        return ProjectRepository(async_session)
    
    @pytest_asyncio.fixture
    async def repo(self, async_session):
        """Create StoryBibleRepository instance."""
        return StoryBibleRepository(async_session)
    
    @pytest_asyncio.fixture
    async def sample_project(self, project_repo):
        """Create a sample project."""
        return await project_repo.create(
            name="Test Project",
            genre="Fantasy",
            target_length=80000
        )
    
    @pytest_asyncio.fixture
    async def sample_bible(self, repo, sample_project):
        """Create a sample story bible."""
        return await repo.create(
            project_id=sample_project.id,
            version=1,
            brief_data={"premise": "Test premise"},
            concept_data={"theme": "Test theme"}
        )
    
    @pytest.mark.asyncio
    async def test_create_story_bible(self, repo, sample_project):
        """Test creating a story bible."""
        bible = await repo.create(
            project_id=sample_project.id,
            version=1,
            brief_data={"premise": "A hero's journey"}
        )
        
        assert bible.id is not None
        assert bible.project_id == sample_project.id
        assert bible.version == 1
    
    @pytest.mark.asyncio
    async def test_get_by_project_id(self, repo, sample_bible):
        """Test getting story bibles by project ID."""
        bibles = await repo.get_by_project_id(sample_bible.project_id)
        
        assert len(bibles) > 0
        assert sample_bible.id in [b.id for b in bibles]
    
    @pytest.mark.asyncio
    async def test_get_latest_by_project(self, repo, sample_bible):
        """Test getting latest story bible."""
        latest = await repo.get_latest_by_project(sample_bible.project_id)
        
        assert latest is not None
        assert latest.id == sample_bible.id
    
    @pytest.mark.asyncio
    async def test_get_by_version(self, repo, sample_bible):
        """Test getting story bible by version."""
        bible = await repo.get_by_version(sample_bible.project_id, 1)
        
        assert bible is not None
        assert bible.version == 1
    
    @pytest.mark.asyncio
    async def test_increment_version(self, repo, sample_bible):
        """Test incrementing version."""
        updated = await repo.increment_version(sample_bible.id)
        
        assert updated is not None
        assert updated.version == 2
    
    @pytest.mark.asyncio
    async def test_update_section(self, repo, sample_bible):
        """Test updating a section."""
        updated = await repo.update_section(
            sample_bible.id,
            "concept",
            {"theme": "Updated theme"}
        )
        
        assert updated is not None
        assert updated.concept_data["theme"] == "Updated theme"


class TestCheckpointRepository:
    """Test CheckpointRepository operations."""
    
    @pytest_asyncio.fixture
    async def project_repo(self, async_session):
        """Create ProjectRepository instance."""
        return ProjectRepository(async_session)
    
    @pytest_asyncio.fixture
    async def repo(self, async_session):
        """Create CheckpointRepository instance."""
        return CheckpointRepository(async_session)
    
    @pytest_asyncio.fixture
    async def sample_project(self, project_repo):
        """Create a sample project."""
        return await project_repo.create(
            name="Test Project",
            genre="Fantasy",
            target_length=80000
        )
    
    @pytest_asyncio.fixture
    async def sample_checkpoint(self, repo, sample_project):
        """Create a sample checkpoint."""
        return await repo.create(
            project_id=sample_project.id,
            checkpoint_type=CheckpointType.CONCEPT,
            status=CheckpointStatus.PENDING,
            prompt="Review the concept",
            context={"theme": "Adventure"}
        )
    
    @pytest.mark.asyncio
    async def test_create_checkpoint(self, repo, sample_project):
        """Test creating a checkpoint."""
        checkpoint = await repo.create(
            project_id=sample_project.id,
            checkpoint_type=CheckpointType.OUTLINE,
            status=CheckpointStatus.PENDING,
            prompt="Review outline"
        )
        
        assert checkpoint.id is not None
        assert checkpoint.checkpoint_type == CheckpointType.OUTLINE
        assert checkpoint.status == CheckpointStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_get_by_project_id(self, repo, sample_checkpoint):
        """Test getting checkpoints by project ID."""
        checkpoints = await repo.get_by_project_id(sample_checkpoint.project_id)
        
        assert len(checkpoints) > 0
        assert sample_checkpoint.id in [c.id for c in checkpoints]
    
    @pytest.mark.asyncio
    async def test_get_pending_checkpoints(self, repo, sample_checkpoint):
        """Test getting pending checkpoints."""
        checkpoints = await repo.get_pending_checkpoints(sample_checkpoint.project_id)
        
        assert len(checkpoints) > 0
        assert all(c.status == CheckpointStatus.PENDING for c in checkpoints)
    
    @pytest.mark.asyncio
    async def test_get_by_type(self, repo, sample_checkpoint):
        """Test getting checkpoints by type."""
        checkpoints = await repo.get_by_type(
            sample_checkpoint.project_id,
            CheckpointType.CONCEPT
        )
        
        assert len(checkpoints) > 0
        assert all(c.checkpoint_type == CheckpointType.CONCEPT for c in checkpoints)
    
    @pytest.mark.asyncio
    async def test_approve(self, repo, sample_checkpoint):
        """Test approving a checkpoint."""
        approved = await repo.approve(sample_checkpoint.id, "Looks good!")
        
        assert approved is not None
        assert approved.status == CheckpointStatus.APPROVED
        assert approved.user_feedback == "Looks good!"
    
    @pytest.mark.asyncio
    async def test_reject(self, repo, sample_checkpoint):
        """Test rejecting a checkpoint."""
        rejected = await repo.reject(sample_checkpoint.id, "Needs work")
        
        assert rejected is not None
        assert rejected.status == CheckpointStatus.REJECTED
        assert rejected.rejection_reason == "Needs work"
    
    @pytest.mark.asyncio
    async def test_skip(self, repo, sample_checkpoint):
        """Test skipping a checkpoint."""
        skipped = await repo.skip(sample_checkpoint.id)
        
        assert skipped is not None
        assert skipped.status == CheckpointStatus.SKIPPED


class TestImageRepository:
    """Test ImageRepository operations."""
    
    @pytest_asyncio.fixture
    async def project_repo(self, async_session):
        """Create ProjectRepository instance."""
        return ProjectRepository(async_session)
    
    @pytest_asyncio.fixture
    async def repo(self, async_session):
        """Create ImageRepository instance."""
        return ImageRepository(async_session)
    
    @pytest_asyncio.fixture
    async def sample_project(self, project_repo):
        """Create a sample project."""
        return await project_repo.create(
            name="Test Project",
            genre="Fantasy",
            target_length=80000
        )
    
    @pytest_asyncio.fixture
    async def sample_image(self, repo, sample_project):
        """Create a sample image."""
        return await repo.create(
            project_id=sample_project.id,
            image_type=ImageType.COVER_ART.value,
            file_path="/path/to/cover.png",
            prompt="Epic fantasy cover",
            model="pixtral-large-latest",
            provider="mistral",
            generation_cost=0.04
        )
    
    @pytest.mark.asyncio
    async def test_create_image(self, repo, sample_project):
        """Test creating an image."""
        image = await repo.create(
            project_id=sample_project.id,
            image_type=ImageType.CHARACTER_PORTRAIT.value,
            file_path="/path/to/portrait.png",
            prompt="Character portrait",
            model="pixtral-large-latest",
            provider="mistral",
            generation_cost=0.02,
            character_name="Hero"
        )
        
        assert image.id is not None
        assert image.image_type == ImageType.CHARACTER_PORTRAIT.value
        assert image.character_name == "Hero"
    
    @pytest.mark.asyncio
    async def test_get_by_project_id(self, repo, sample_image):
        """Test getting images by project ID."""
        images = await repo.get_by_project_id(sample_image.project_id)
        
        assert len(images) > 0
        assert sample_image.id in [i.id for i in images]
    
    @pytest.mark.asyncio
    async def test_get_by_type(self, repo, sample_image):
        """Test getting images by type."""
        images = await repo.get_by_type(
            sample_image.project_id,
            ImageType.COVER_ART.value
        )
        
        assert len(images) > 0
        assert all(i.image_type == ImageType.COVER_ART.value for i in images)
    
    @pytest.mark.asyncio
    async def test_get_cover_art(self, repo, sample_image):
        """Test getting cover art."""
        cover = await repo.get_cover_art(sample_image.project_id)
        
        assert cover is not None
        assert cover.image_type == ImageType.COVER_ART.value
    
    @pytest.mark.asyncio
    async def test_get_total_cost(self, repo, sample_image):
        """Test calculating total cost."""
        total = await repo.get_total_cost(sample_image.project_id)
        
        assert total > 0
        assert total == 0.04


class TestWorkflowStateRepository:
    """Test WorkflowStateRepository operations."""
    
    @pytest_asyncio.fixture
    async def project_repo(self, async_session):
        """Create ProjectRepository instance."""
        return ProjectRepository(async_session)
    
    @pytest_asyncio.fixture
    async def repo(self, async_session):
        """Create WorkflowStateRepository instance."""
        return WorkflowStateRepository(async_session)
    
    @pytest_asyncio.fixture
    async def sample_project(self, project_repo):
        """Create a sample project."""
        return await project_repo.create(
            name="Test Project",
            genre="Fantasy",
            target_length=80000
        )
    
    @pytest_asyncio.fixture
    async def sample_state(self, repo, sample_project):
        """Create a sample workflow state."""
        return await repo.create(
            project_id=sample_project.id,
            status=WorkflowStatus.PENDING,
            current_step="initialization",
            progress_percentage=0
        )
    
    @pytest.mark.asyncio
    async def test_create_workflow_state(self, repo, sample_project):
        """Test creating a workflow state."""
        state = await repo.create(
            project_id=sample_project.id,
            status=WorkflowStatus.RUNNING,
            current_step="concept",
            progress_percentage=10
        )
        
        assert state.id is not None
        assert state.status == WorkflowStatus.RUNNING
        assert state.current_step == "concept"
    
    @pytest.mark.asyncio
    async def test_get_by_project_id(self, repo, sample_state):
        """Test getting workflow state by project ID."""
        state = await repo.get_by_project_id(sample_state.project_id)
        
        assert state is not None
        assert state.id == sample_state.id
    
    @pytest.mark.asyncio
    async def test_start(self, repo, sample_state):
        """Test starting a workflow."""
        started = await repo.start(sample_state.id)
        
        assert started is not None
        assert started.status == WorkflowStatus.RUNNING
        assert started.started_at is not None
    
    @pytest.mark.asyncio
    async def test_pause(self, repo, sample_state):
        """Test pausing a workflow."""
        await repo.start(sample_state.id)
        paused = await repo.pause(sample_state.id)
        
        assert paused is not None
        assert paused.status == WorkflowStatus.PAUSED
    
    @pytest.mark.asyncio
    async def test_resume(self, repo, sample_state):
        """Test resuming a workflow."""
        await repo.start(sample_state.id)
        await repo.pause(sample_state.id)
        resumed = await repo.resume(sample_state.id)
        
        assert resumed is not None
        assert resumed.status == WorkflowStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_complete(self, repo, sample_state):
        """Test completing a workflow."""
        await repo.start(sample_state.id)
        completed = await repo.complete(sample_state.id)
        
        assert completed is not None
        assert completed.status == WorkflowStatus.COMPLETED
        assert completed.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_fail(self, repo, sample_state):
        """Test failing a workflow."""
        await repo.start(sample_state.id)
        failed = await repo.fail(sample_state.id, "Test error")
        
        assert failed is not None
        assert failed.status == WorkflowStatus.FAILED
        assert failed.error_message == "Test error"
    
    @pytest.mark.asyncio
    async def test_update_progress(self, repo, sample_state):
        """Test updating progress."""
        updated = await repo.update_progress(sample_state.id, "outline", 25)
        
        assert updated is not None
        assert updated.current_step == "outline"
        assert updated.progress_percentage == 25
    
    @pytest.mark.asyncio
    async def test_get_or_create_for_project(self, repo, sample_project):
        """Test get or create for project."""
        state1, created1 = await repo.get_or_create_for_project(sample_project.id)
        assert created1 is True
        
        state2, created2 = await repo.get_or_create_for_project(sample_project.id)
        assert created2 is False
        assert state1.id == state2.id

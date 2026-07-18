"""Unit tests for SQLAlchemy models."""
import pytest
from datetime import datetime
from decimal import Decimal

from storytelling_workspace.db.models import (
    Project,
    StoryBible,
    Chapter,
    Checkpoint,
    Image,
    WorkflowState,
    AgentDelta,
    APICost,
)


class TestProject:
    """Tests for Project model."""
    
    def test_create_project(self):
        """Test creating a project instance."""
        project = Project(
            name="Test Novel",
            description="A test project",
            genre="Fantasy",
            target_length=80000,
            status="draft"
        )
        
        assert project.name == "Test Novel"
        assert project.description == "A test project"
        assert project.genre == "Fantasy"
        assert project.target_length == 80000
        assert project.status == "draft"
        # Note: ID is generated on database insert, not instantiation
    
    def test_soft_delete(self):
        """Test soft delete functionality."""
        project = Project(name="Test")
        assert not project.is_deleted
        
        project.soft_delete()
        assert project.is_deleted
        assert project.deleted_at is not None
        
        project.restore()
        assert not project.is_deleted
        assert project.deleted_at is None


class TestStoryBible:
    """Tests for StoryBible model."""
    
    def test_create_story_bible(self):
        """Test creating a story bible instance."""
        story_bible = StoryBible(
            project_id="test-project-id",
            version=1,
            brief={"title": "Test Novel", "premise": "A test story"},
            concept={"theme": "Adventure"},
            characters={"protagonist": {"name": "Hero"}}
        )
        
        assert story_bible.project_id == "test-project-id"
        assert story_bible.version == 1
        assert story_bible.brief["title"] == "Test Novel"
        assert story_bible.concept["theme"] == "Adventure"
        assert story_bible.characters["protagonist"]["name"] == "Hero"


class TestChapter:
    """Tests for Chapter model."""
    
    def test_create_chapter(self):
        """Test creating a chapter instance."""
        chapter = Chapter(
            story_bible_id="test-bible-id",
            chapter_number=1,
            title="The Beginning",
            content="Once upon a time...",
            word_count=100,
            target_word_count=3000,
            status="completed"
        )
        
        assert chapter.story_bible_id == "test-bible-id"
        assert chapter.chapter_number == 1
        assert chapter.title == "The Beginning"
        assert chapter.content == "Once upon a time..."
        assert chapter.word_count == 100
        assert chapter.status == "completed"


class TestCheckpoint:
    """Tests for Checkpoint model."""
    
    def test_create_checkpoint(self):
        """Test creating a checkpoint instance."""
        checkpoint = Checkpoint(
            project_id="test-project-id",
            story_bible_id="test-bible-id",
            checkpoint_type="concept",
            phase="concept_development",
            agent_name="ConceptAgent",
            status="pending",
            content={"concept": "Test concept"}
        )
        
        assert checkpoint.project_id == "test-project-id"
        assert checkpoint.checkpoint_type == "concept"
        assert checkpoint.phase == "concept_development"
        assert checkpoint.agent_name == "ConceptAgent"
        assert checkpoint.status == "pending"
        assert checkpoint.content["concept"] == "Test concept"


class TestImage:
    """Tests for Image model."""
    
    def test_create_image(self):
        """Test creating an image instance."""
        image = Image(
            project_id="test-project-id",
            story_bible_id="test-bible-id",
            image_type="cover_art",
            file_path="images/cover.png",
            file_size=1024000,
            prompt="A fantasy book cover",
            model="pixtral-12b-2409",
            provider="mistral",
            width=1024,
            height=1024,
            format="png",
            generation_cost=Decimal("0.0400")
        )
        
        assert image.image_type == "cover_art"
        assert image.file_path == "images/cover.png"
        assert image.file_size == 1024000
        assert image.width == 1024
        assert image.height == 1024
        assert image.generation_cost == Decimal("0.0400")


class TestWorkflowState:
    """Tests for WorkflowState model."""
    
    def test_create_workflow_state(self):
        """Test creating a workflow state instance."""
        workflow = WorkflowState(
            project_id="test-project-id",
            current_phase="concept_development",
            current_agent="ConceptAgent",
            status="running",
            total_steps=10,
            completed_steps=3,
            progress_percentage=Decimal("30.00")
        )
        
        assert workflow.current_phase == "concept_development"
        assert workflow.current_agent == "ConceptAgent"
        assert workflow.status == "running"
        assert workflow.total_steps == 10
        assert workflow.completed_steps == 3
        assert workflow.progress_percentage == Decimal("30.00")


class TestAgentDelta:
    """Tests for AgentDelta model."""
    
    def test_create_agent_delta(self):
        """Test creating an agent delta instance."""
        delta = AgentDelta(
            story_bible_id="test-bible-id",
            agent_name="ConceptAgent",
            agent_version="1.0.0",
            changes={"added": ["theme"], "modified": []},
            summary="Added theme to concept",
            execution_time_ms=1500,
            tokens_used=500,
            cost=Decimal("0.0125")
        )
        
        assert delta.agent_name == "ConceptAgent"
        assert delta.agent_version == "1.0.0"
        assert delta.changes["added"] == ["theme"]
        assert delta.execution_time_ms == 1500
        assert delta.tokens_used == 500
        assert delta.cost == Decimal("0.0125")


class TestAPICost:
    """Tests for APICost model."""
    
    def test_create_api_cost(self):
        """Test creating an API cost instance."""
        api_cost = APICost(
            project_id="test-project-id",
            provider="mistral",
            model="mistral-large-latest",
            api_type="text",
            tokens_used=1000,
            cost=Decimal("0.0250"),
            success=True
        )
        
        assert api_cost.provider == "mistral"
        assert api_cost.model == "mistral-large-latest"
        assert api_cost.api_type == "text"
        assert api_cost.tokens_used == 1000
        assert api_cost.cost == Decimal("0.0250")
        assert api_cost.success is True
    
    def test_create_failed_api_cost(self):
        """Test creating a failed API cost instance."""
        api_cost = APICost(
            project_id="test-project-id",
            provider="openai",
            model="gpt-4",
            api_type="text",
            cost=Decimal("0.0000"),
            success=False,
            error_message="Rate limit exceeded"
        )
        
        assert api_cost.success is False
        assert api_cost.error_message == "Rate limit exceeded"

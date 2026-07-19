import pytest
import pytest_asyncio
from uuid import uuid4

from storytelling_workspace.db.models.project import Project, ProjectStatus
from storytelling_workspace.db.repositories.project import ProjectRepository

from storytelling_workspace.db.models.story_bible import StoryBible
from storytelling_workspace.db.repositories.story_bible import StoryBibleRepository

from storytelling_workspace.db.models.checkpoint import Checkpoint, CheckpointStatus, CheckpointType
from storytelling_workspace.db.repositories.checkpoint import CheckpointRepository

from storytelling_workspace.db.models.image import Image, ImageType
from storytelling_workspace.db.repositories.image import ImageRepository

from storytelling_workspace.db.models.workflow_state import WorkflowState, WorkflowStatus
from storytelling_workspace.db.repositories.workflow_state import WorkflowStateRepository


@pytest.mark.asyncio
async def test_project_repository(async_session):
    repo = ProjectRepository(async_session)
    
    # Create
    project = await repo.create(
        name="Test Project",
        description="A test project",
        genre="Sci-Fi",
        target_length=80000
    )
    assert project.id is not None
    assert project.name == "Test Project"
    
    # Read
    fetched = await repo.get_by_id(project.id)
    assert fetched is not None
    assert fetched.name == "Test Project"
    
    # Update
    updated = await repo.update(project.id, name="Updated Project")
    assert updated.name == "Updated Project"
    
    # Delete
    deleted = await repo.delete(project.id)
    assert deleted is True

@pytest.mark.asyncio
async def test_story_bible_repository(async_session):
    repo = StoryBibleRepository(async_session)
    project_repo = ProjectRepository(async_session)
    
    project = await project_repo.create(name="Project for StoryBible")
    
    # Create
    story_bible = await repo.create(
        project_id=project.id,
        characters={"list": []},
        world_rules={"rules": []}
    )
    assert story_bible.id is not None
    
    # Read
    fetched = await repo.get_by_id(story_bible.id)
    assert fetched is not None
    
    # Update
    updated = await repo.update(story_bible.id, characters={"list": ["Alice"]})
    assert updated.characters == {"list": ["Alice"]}
    
    # Delete
    await repo.delete(story_bible.id)
    assert await repo.get_by_id(story_bible.id) is None

@pytest.mark.asyncio
async def test_checkpoint_repository(async_session):
    repo = CheckpointRepository(async_session)
    project_repo = ProjectRepository(async_session)
    sb_repo = StoryBibleRepository(async_session)
    
    project = await project_repo.create(name="Project for Checkpoint")
    sb = await sb_repo.create(project_id=project.id)
    
    # Create
    checkpoint = await repo.create(
        project_id=project.id,
        story_bible_id=sb.id,
        checkpoint_type=CheckpointType.CONCEPT,
        phase="concept_phase",
        agent_name="ConceptAgent",
        content={"key": "value"}
    )
    assert checkpoint.id is not None
    
    # Read
    fetched = await repo.get_by_id(checkpoint.id)
    assert fetched is not None
    assert fetched.content == {"key": "value"}
    
    # Update
    updated = await repo.update(checkpoint.id, content={"key": "updated"})
    assert updated.content == {"key": "updated"}
    
    # Delete
    await repo.delete(checkpoint.id)

@pytest.mark.asyncio
async def test_image_repository(async_session):
    repo = ImageRepository(async_session)
    project_repo = ProjectRepository(async_session)
    sb_repo = StoryBibleRepository(async_session)
    
    project = await project_repo.create(name="Project for Image")
    sb = await sb_repo.create(project_id=project.id)
    
    # Create
    image = await repo.create(
        project_id=project.id,
        story_bible_id=sb.id,
        image_type=ImageType.COVER_ART.value,
        file_path="/tmp/test.png",
        file_size=1024,
        prompt="A cool image",
        model="pixtral",
        provider="mistral",
        width=1024,
        height=1024,
        format="png"
    )
    assert image.id is not None
    
    # Read
    fetched = await repo.get_by_id(image.id)
    assert fetched is not None
    assert fetched.prompt == "A cool image"
    
    # Update
    updated = await repo.update(image.id, prompt="Updated prompt")
    assert updated.prompt == "Updated prompt"
    
    # Delete
    await repo.delete(image.id)

@pytest.mark.asyncio
async def test_workflow_state_repository(async_session):
    repo = WorkflowStateRepository(async_session)
    project_repo = ProjectRepository(async_session)
    
    project = await project_repo.create(name="Project for Workflow")
    
    # Create
    state = await repo.create(
        project_id=project.id,
        current_phase="concept",
        total_steps=10
    )
    assert state.id is not None
    
    # Read
    fetched = await repo.get_by_id(state.id)
    assert fetched is not None
    assert fetched.current_phase == "concept"
    
    # Update
    updated = await repo.update(state.id, current_phase="outline")
    assert updated.current_phase == "outline"
    
    # Delete
    await repo.delete(state.id)

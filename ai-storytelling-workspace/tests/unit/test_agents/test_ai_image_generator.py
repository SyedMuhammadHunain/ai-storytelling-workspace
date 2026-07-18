"""Unit tests for AI Image Generator Agent."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import tempfile
import shutil

from storytelling_workspace.agents.ai_image_generator import AIImageGeneratorAgent
from storytelling_workspace.story_bible import StoryBible
from storytelling_workspace.models import BookBrief, Concept, Character, Chapter, WorldRules
from storytelling_workspace.core.image_provider import ImageResponse


@pytest.fixture(autouse=True)
def mock_api_keys():
    """Mock API keys for all tests."""
    with patch.dict('os.environ', {'MISTRAL_API_KEY': 'test_mistral_key', 'OPENAI_API_KEY': 'test_openai_key'}):
        yield


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_bible():
    """Create sample Story Bible with full content."""
    bible = StoryBible()
    
    # Brief
    bible.brief = BookBrief(
        genre="Fantasy",
        premise="A young apprentice discovers ancient magic",
        tone="Epic and adventurous",
        target_length=100000
    )
    
    # Concept
    bible.concept = Concept(
        logline="When a young apprentice discovers ancient magic, they must master their powers to save the kingdom.",
        premise=bible.brief.premise,
        central_conflict="The protagonist must overcome self-doubt while facing a powerful enemy.",
        theme="Courage in the face of overwhelming odds"
    )
    
    # Characters
    bible.add_character(Character(
        name="Aria Stormwind",
        role="protagonist",
        physical_description="17 years old, dark curly hair, green eyes",
        backstory="Orphaned apprentice",
        goals=["Master magic", "Save kingdom"],
        flaws=["Self-doubt"],
        arc="Becomes confident hero",
        voice_signature="Direct and earnest"
    ))
    
    bible.add_character(Character(
        name="Lord Malachar",
        role="antagonist",
        physical_description="Tall, gaunt, pale skin, dark robes",
        backstory="Exiled advisor",
        goals=["Reclaim power"],
        flaws=["Arrogance"],
        arc="Descends into darkness",
        voice_signature="Formal and commanding"
    ))
    
    # World rules
    bible.world_rules = WorldRules(
        magic_system="Elemental magic",
        technology_level="Medieval",
        social_structure="Kingdom with nobility",
        key_rules=["Magic requires training", "Dark magic corrupts"]
    )
    
    # Chapters (chapters is a dict, not a list)
    for i in range(1, 6):
        chapter = Chapter(
            number=i,
            title=f"Chapter {i}",
            pov="Aria Stormwind",
            goal=f"Goal for chapter {i}",
            conflict=f"Conflict in chapter {i}",
            word_count_target=3000
        )
        bible.chapters[i] = chapter
    
    return bible


@pytest.fixture
def mock_image_response():
    """Create mock image response."""
    return ImageResponse(
        image_data=b"fake_image_data",
        model="pixtral-large-latest",
        provider="mistral",
        size="1024x1024",
        format="png",
        cost=0.05,
        compressed_size=len(b"fake_image_data")
    )


class TestAIImageGeneratorAgent:
    """Test AI Image Generator Agent."""
    
    def test_initialization(self, temp_output_dir):
        """Test agent initialization."""
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir)
        
        assert agent.name == "AI Image Generator Agent"
        assert agent.model == "pixtral-large-latest"
        assert agent.output_dir == Path(temp_output_dir)
        assert agent.generate_cover is True
        assert agent.generate_portraits is True
        assert agent.generate_scenes is True
        assert agent.max_portraits == 5
        assert agent.max_scenes == 10
    
    def test_initialization_custom_settings(self, temp_output_dir):
        """Test agent initialization with custom settings."""
        agent = AIImageGeneratorAgent(
            output_dir=temp_output_dir,
            generate_cover=False,
            generate_portraits=True,
            generate_scenes=False,
            max_portraits=3,
            max_scenes=5
        )
        
        assert agent.generate_cover is False
        assert agent.generate_portraits is True
        assert agent.generate_scenes is False
        assert agent.max_portraits == 3
        assert agent.max_scenes == 5
    
    def test_output_directory_created(self, temp_output_dir):
        """Test that output directory is created."""
        output_path = Path(temp_output_dir) / "test_images"
        agent = AIImageGeneratorAgent(output_dir=str(output_path))
        
        assert output_path.exists()
        assert output_path.is_dir()
    
    @pytest.mark.asyncio
    async def test_generate_image(self, temp_output_dir, mock_image_response):
        """Test generating a single image."""
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir)
        
        # Mock the image factory
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(return_value=mock_image_response)):
            response = await agent.generate_image(
                prompt="Test prompt",
                size="1024x1024",
                filename="test.png"
            )
        
        assert response.image_data == b"fake_image_data"
        assert response.cost == 0.05
        
        # Verify file was saved
        output_file = Path(temp_output_dir) / "test.png"
        assert output_file.exists()
        assert output_file.read_bytes() == b"fake_image_data"
    
    @pytest.mark.asyncio
    async def test_generate_cover_art(self, temp_output_dir, sample_bible, mock_image_response):
        """Test cover art generation."""
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir)
        
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(return_value=mock_image_response)):
            result = await agent._generate_cover_art(sample_bible)
        
        assert result is not None
        assert result["type"] == "cover_art"
        assert result["size"] == "1024x1024"
        assert result["cost"] == 0.05
        assert "cover_art.png" in result["path"]
    
    @pytest.mark.asyncio
    async def test_generate_cover_art_no_concept(self, temp_output_dir, mock_image_response):
        """Test cover art generation without concept."""
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir)
        bible = StoryBible()
        bible.brief = BookBrief(genre="Fantasy", premise="Test")
        bible.concept = None  # Explicitly set to None
        
        # Mock the factory even though we expect early return
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(return_value=mock_image_response)):
            result = await agent._generate_cover_art(bible)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_generate_character_portraits(self, temp_output_dir, sample_bible, mock_image_response):
        """Test character portrait generation."""
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir, max_portraits=2)
        
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(return_value=mock_image_response)):
            results = await agent._generate_character_portraits(sample_bible)
        
        assert len(results) == 2  # max_portraits=2
        assert results[0]["type"] == "character_portrait"
        assert results[0]["size"] == "512x512"
        assert results[0]["character"] in ["Aria Stormwind", "Lord Malachar"]
    
    @pytest.mark.asyncio
    async def test_generate_character_portraits_no_characters(self, temp_output_dir):
        """Test character portrait generation without characters."""
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir)
        bible = StoryBible()
        
        results = await agent._generate_character_portraits(bible)
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_generate_scene_illustrations(self, temp_output_dir, sample_bible, mock_image_response):
        """Test scene illustration generation."""
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir, max_scenes=3)
        
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(return_value=mock_image_response)):
            results = await agent._generate_scene_illustrations(sample_bible)
        
        assert len(results) == 3  # max_scenes=3
        assert results[0]["type"] == "scene_illustration"
        assert results[0]["size"] == "1024x512"
        assert "chapter" in results[0]
    
    @pytest.mark.asyncio
    async def test_generate_scene_illustrations_no_chapters(self, temp_output_dir):
        """Test scene illustration generation without chapters."""
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir)
        bible = StoryBible()
        
        results = await agent._generate_scene_illustrations(bible)
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_execute_all_images(self, temp_output_dir, sample_bible, mock_image_response):
        """Test full execution generating all image types."""
        agent = AIImageGeneratorAgent(
            output_dir=temp_output_dir,
            max_portraits=2,
            max_scenes=2
        )
        
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(return_value=mock_image_response)):
            result = await agent.execute(sample_bible)
        
        assert result["success"] is True
        assert result["total_images"] == 5  # 1 cover + 2 portraits + 2 scenes
        assert len(result["images"]) == 5
        assert result["total_cost"] == 0.25  # 5 * 0.05
    
    @pytest.mark.asyncio
    async def test_execute_cover_only(self, temp_output_dir, sample_bible, mock_image_response):
        """Test execution with only cover art."""
        agent = AIImageGeneratorAgent(
            output_dir=temp_output_dir,
            generate_cover=True,
            generate_portraits=False,
            generate_scenes=False
        )
        
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(return_value=mock_image_response)):
            result = await agent.execute(sample_bible)
        
        assert result["success"] is True
        assert result["total_images"] == 1
        assert result["images"][0]["type"] == "cover_art"
    
    @pytest.mark.asyncio
    async def test_execute_portraits_only(self, temp_output_dir, sample_bible, mock_image_response):
        """Test execution with only character portraits."""
        agent = AIImageGeneratorAgent(
            output_dir=temp_output_dir,
            generate_cover=False,
            generate_portraits=True,
            generate_scenes=False,
            max_portraits=2
        )
        
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(return_value=mock_image_response)):
            result = await agent.execute(sample_bible)
        
        assert result["success"] is True
        assert result["total_images"] == 2
        assert all(img["type"] == "character_portrait" for img in result["images"])
    
    @pytest.mark.asyncio
    async def test_execute_error_handling(self, temp_output_dir, sample_bible):
        """Test error handling during execution."""
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir)
        
        # Mock image factory to raise exception
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(side_effect=Exception("API Error"))):
            result = await agent.execute(sample_bible)
        
        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "API Error"
        assert result["error_type"] == "Exception"
    
    @pytest.mark.asyncio
    async def test_story_bible_updated(self, temp_output_dir, sample_bible, mock_image_response):
        """Test that Story Bible is updated with image information."""
        agent = AIImageGeneratorAgent(
            output_dir=temp_output_dir,
            generate_cover=True,
            generate_portraits=False,
            generate_scenes=False
        )
        
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(return_value=mock_image_response)):
            result = await agent.execute(sample_bible)
        
        # Check that changes were recorded
        assert len(sample_bible.deltas) > 0
        last_delta = sample_bible.deltas[-1]
        assert last_delta.agent_name == "AI Image Generator Agent"
        assert "images_generated" in last_delta.changes
    
    @pytest.mark.asyncio
    async def test_character_priority_ordering(self, temp_output_dir, sample_bible, mock_image_response):
        """Test that characters are prioritized correctly (protagonist, antagonist, supporting)."""
        # Add a supporting character
        sample_bible.add_character(Character(
            name="Mentor",
            role="supporting",
            physical_description="Wise old mage",
            backstory="Former hero",
            goals=["Guide protagonist"],
            flaws=["Haunted by past"],
            arc="Redemption",
            voice_signature="Thoughtful"
        ))
        
        agent = AIImageGeneratorAgent(output_dir=temp_output_dir, max_portraits=2)
        
        generated_names = []
        
        async def mock_generate(prompt, **kwargs):
            # Extract character name from prompt
            if "Aria" in prompt:
                generated_names.append("Aria Stormwind")
            elif "Malachar" in prompt:
                generated_names.append("Lord Malachar")
            elif "Mentor" in prompt:
                generated_names.append("Mentor")
            return mock_image_response
        
        with patch.object(agent._image_factory, 'generate_image', new=AsyncMock(side_effect=mock_generate)):
            await agent._generate_character_portraits(sample_bible)
        
        # Should generate protagonist and antagonist first
        assert len(generated_names) == 2
        assert "Aria Stormwind" in generated_names
        assert "Lord Malachar" in generated_names

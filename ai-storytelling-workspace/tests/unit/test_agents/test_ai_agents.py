"""Unit tests for AI-powered agents."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
import os

from storytelling_workspace.agents.ai_agent import AIAgent
from storytelling_workspace.agents.ai_concept import AIConceptAgent
from storytelling_workspace.agents.ai_character import AICharacterAgent
from storytelling_workspace.story_bible import StoryBible
from storytelling_workspace.models import BookBrief, Concept, Character
from storytelling_workspace.core.ai_provider import AIResponse


@pytest.fixture(autouse=True)
def mock_api_keys():
    """Mock API keys for all tests."""
    with patch.dict('os.environ', {'MISTRAL_API_KEY': 'test_mistral_key', 'OPENAI_API_KEY': 'test_openai_key'}):
        yield


@pytest.fixture
def sample_bible():
    """Create sample Story Bible for testing."""
    bible = StoryBible()
    bible.brief = BookBrief(
        genre="Fantasy",
        premise="A young apprentice discovers ancient magic",
        tone="Epic and adventurous",
        target_length=100000
    )
    bible.concept = Concept(
        logline="When a young apprentice discovers ancient magic, they must master their powers to save the kingdom.",
        premise=bible.brief.premise,
        central_conflict="The protagonist must overcome self-doubt while facing a powerful enemy.",
        theme="Courage in the face of overwhelming odds"
    )
    return bible


@pytest.fixture
def mock_ai_response():
    """Create mock AI response."""
    return AIResponse(
        content='{"logline": "Test logline", "central_conflict": "Test conflict", "theme": "Test theme"}',
        model="mistral-large-latest",
        provider="mistral",
        tokens_used=100,
        input_tokens=50,
        output_tokens=50,
        cached=False,
        cost=0.01
    )


class TestAIAgent:
    """Test AIAgent base class."""
    
    def test_initialization(self):
        """Test AI agent initialization."""
        # Create a concrete implementation for testing
        class TestAgent(AIAgent):
            def build_prompt(self, bible, **kwargs):
                return "test prompt"
            
            def parse_response(self, response, bible):
                return {"test": "data"}
        
        agent = TestAgent(name="Test Agent")
        assert agent.name == "Test Agent"
        assert agent.model == "mistral-large-latest"
        assert agent.temperature == 0.7
        assert agent.max_tokens == 2000
    
    def test_shared_resources_initialized(self):
        """Test that shared resources are initialized."""
        # Shared resources are initialized on first agent creation
        # This test verifies they exist after any agent is created
        class TestAgent(AIAgent):
            def build_prompt(self, bible, **kwargs):
                return "test"
            def parse_response(self, response, bible):
                return {}
        
        # Create agent (will initialize shared resources if not already done)
        agent = TestAgent(name="Test")
        
        # Verify agent has access to shared resources through class
        assert hasattr(AIAgent, '_ai_factory')
        assert hasattr(AIAgent, '_rate_limiter')
        assert hasattr(AIAgent, '_cache')
        assert hasattr(AIAgent, '_cost_tracker')


class TestAIConceptAgent:
    """Test AI Concept Agent."""
    
    @pytest.mark.asyncio
    async def test_build_prompt(self, sample_bible):
        """Test prompt building."""
        agent = AIConceptAgent()
        prompt = agent.build_prompt(sample_bible)
        
        assert "Fantasy" in prompt
        assert "young apprentice" in prompt
        assert "logline" in prompt.lower()
        assert "theme" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_parse_response_json(self, sample_bible, mock_ai_response):
        """Test parsing JSON response."""
        agent = AIConceptAgent()
        result = agent.parse_response(mock_ai_response, sample_bible)
        
        assert "concept" in result
        assert result["logline"] == "Test logline"
        assert result["theme"] == "Test theme"
        assert sample_bible.concept.logline == "Test logline"
    
    @pytest.mark.asyncio
    async def test_parse_response_with_markdown(self, sample_bible):
        """Test parsing response with markdown code blocks."""
        agent = AIConceptAgent()
        
        response = AIResponse(
            content='```json\n{"logline": "Markdown logline", "central_conflict": "Conflict", "theme": "Theme"}\n```',
            model="test",
            provider="test",
            tokens_used=100,
            cost=0.01
        )
        
        result = agent.parse_response(response, sample_bible)
        
        assert result["logline"] == "Markdown logline"
        assert sample_bible.concept.logline == "Markdown logline"
    
    @pytest.mark.asyncio
    async def test_parse_response_fallback(self, sample_bible):
        """Test fallback parsing when JSON fails."""
        agent = AIConceptAgent()
        
        response = AIResponse(
            content='**Logline:** Fallback logline\n**Theme:** Fallback theme',
            model="test",
            provider="test",
            tokens_used=100,
            cost=0.01
        )
        
        result = agent.parse_response(response, sample_bible)
        
        assert "concept" in result
        assert "warning" in result
        assert sample_bible.concept is not None
    
    @pytest.mark.asyncio
    async def test_execute_success(self, sample_bible):
        """Test successful execution."""
        agent = AIConceptAgent()
        
        # Mock the generate_text method
        mock_response = AIResponse(
            content='{"logline": "AI logline", "central_conflict": "AI conflict", "theme": "AI theme"}',
            model="mistral-large-latest",
            provider="mistral",
            tokens_used=150,
            cost=0.02
        )
        
        with patch.object(agent, 'generate_text', new=AsyncMock(return_value=mock_response)):
            result = await agent.execute(sample_bible)
        
        assert result["success"] is True
        assert "data" in result
        assert result["tokens_used"] == 150
        assert result["cost"] == 0.02
        assert sample_bible.concept.logline == "AI logline"


class TestAICharacterAgent:
    """Test AI Character Agent."""
    
    @pytest.mark.asyncio
    async def test_build_prompt(self, sample_bible):
        """Test prompt building for character."""
        agent = AICharacterAgent()
        prompt = agent.build_prompt(sample_bible, role="protagonist")
        
        assert "protagonist" in prompt
        assert sample_bible.concept.logline in prompt
        assert sample_bible.brief.genre in prompt
    
    @pytest.mark.asyncio
    async def test_parse_character_response(self):
        """Test parsing character response."""
        agent = AICharacterAgent()
        
        response = AIResponse(
            content=json.dumps({
                "name": "Test Hero",
                "role": "protagonist",
                "physical_description": "Tall and brave",
                "backstory": "Orphaned as a child",
                "goals": ["Save the kingdom", "Master magic"],
                "flaws": ["Self-doubt", "Impulsive"],
                "arc": "From uncertain to confident",
                "voice_signature": "Direct and earnest"
            }),
            model="test",
            provider="test",
            tokens_used=200,
            cost=0.03
        )
        
        result = agent._parse_character_response(response)
        
        assert result["name"] == "Test Hero"
        assert len(result["goals"]) == 2
        assert len(result["flaws"]) == 2
        assert result["arc"] == "From uncertain to confident"
    
    @pytest.mark.asyncio
    async def test_create_character(self, sample_bible):
        """Test creating a single character."""
        agent = AICharacterAgent()
        
        # Mock the generate_text method
        mock_response = AIResponse(
            content=json.dumps({
                "name": "Aria Stormwind",
                "role": "protagonist",
                "physical_description": "17 years old, dark hair",
                "backstory": "Orphaned apprentice",
                "goals": ["Master magic", "Save kingdom"],
                "flaws": ["Self-doubt", "Impulsive"],
                "arc": "Becomes confident hero",
                "voice_signature": "Direct and earnest"
            }),
            model="mistral-large-latest",
            provider="mistral",
            tokens_used=250,
            cost=0.04
        )
        
        with patch.object(agent, 'generate_text', new=AsyncMock(return_value=mock_response)):
            character = await agent._create_character(sample_bible, "protagonist")
        
        assert isinstance(character, Character)
        assert character.name == "Aria Stormwind"
        assert character.role == "protagonist"
        assert len(character.goals) == 2
        assert len(character.flaws) == 2
    
    @pytest.mark.asyncio
    async def test_execute_creates_multiple_characters(self, sample_bible):
        """Test that execute creates protagonist, antagonist, and supporting characters."""
        agent = AICharacterAgent()
        
        # Track call count for unique names
        call_count = [0]
        
        # Mock responses for different character types
        def mock_generate(prompt, **kwargs):
            call_count[0] += 1
            if "protagonist" in prompt:
                content = json.dumps({
                    "name": "Hero",
                    "role": "protagonist",
                    "physical_description": "Brave",
                    "backstory": "Orphan",
                    "goals": ["Save world"],
                    "flaws": ["Doubt"],
                    "arc": "Growth",
                    "voice_signature": "Direct"
                })
            elif "antagonist" in prompt:
                content = json.dumps({
                    "name": "Villain",
                    "role": "antagonist",
                    "physical_description": "Dark",
                    "backstory": "Exiled",
                    "goals": ["Conquer"],
                    "flaws": ["Arrogance"],
                    "arc": "Descent",
                    "voice_signature": "Formal"
                })
            else:
                # Generate unique names for supporting characters
                content = json.dumps({
                    "name": f"Supporting{call_count[0]}",
                    "role": "supporting",
                    "physical_description": "Wise",
                    "backstory": "Former hero",
                    "goals": ["Guide hero"],
                    "flaws": ["Haunted"],
                    "arc": "Redemption",
                    "voice_signature": "Thoughtful"
                })
            
            return AIResponse(
                content=content,
                model="test",
                provider="test",
                tokens_used=200,
                cost=0.03
            )
        
        with patch.object(agent, 'generate_text', new=AsyncMock(side_effect=mock_generate)):
            result = await agent.execute(sample_bible)
        
        assert result["success"] is True
        assert result["characters_count"] == 4  # protagonist + antagonist + 2 supporting
        assert len(sample_bible.characters) == 4


class TestAIAgentIntegration:
    """Integration tests for AI agents."""
    
    @pytest.mark.asyncio
    async def test_cost_tracking(self, sample_bible):
        """Test that cost tracking works across agents."""
        agent = AIConceptAgent()
        
        # Mock execution
        mock_response = AIResponse(
            content='{"logline": "Test", "central_conflict": "Test", "theme": "Test"}',
            model="test",
            provider="test",
            tokens_used=100,
            cost=0.01
        )
        
        with patch.object(agent, 'generate_text', new=AsyncMock(return_value=mock_response)):
            result = await agent.execute(sample_bible)
        
        # Check that execution tracked cost
        assert result["success"] is True
        assert result["cost"] == 0.01
        assert result["tokens_used"] == 100
        
        # Check that cost tracker has stats
        stats = AIAgent.get_cost_stats()
        assert isinstance(stats, dict)

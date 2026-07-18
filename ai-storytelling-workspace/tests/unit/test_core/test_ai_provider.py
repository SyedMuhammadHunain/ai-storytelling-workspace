"""Unit tests for AI provider abstraction layer."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from storytelling_workspace.core.ai_provider import (
    AIProvider,
    MistralProvider,
    OpenAIProvider,
    AIProviderFactory,
    AIResponse
)
from storytelling_workspace.core.exceptions import (
    APIKeyError,
    RateLimitError,
    ModelNotFoundError,
    ContentGenerationError
)
from storytelling_workspace.core.rate_limiter import RateLimiter, RateLimitConfig
from storytelling_workspace.core.cache import InMemoryCache
from storytelling_workspace.core.cost_tracker import CostTracker


@pytest.fixture
def mock_rate_limiter():
    """Create mock rate limiter."""
    limiter = Mock(spec=RateLimiter)
    limiter.acquire = AsyncMock()
    limiter.record_usage = Mock()
    return limiter


@pytest.fixture
def mock_cache():
    """Create mock cache."""
    cache = Mock(spec=InMemoryCache)
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    return cache


@pytest.fixture
def mock_cost_tracker():
    """Create mock cost tracker."""
    tracker = Mock(spec=CostTracker)
    tracker.record_call = Mock(return_value=0.05)
    return tracker


class TestAIProvider:
    """Test AIProvider base class."""
    
    def test_init_without_api_key_raises_error(self):
        """Test that initializing without API key raises error."""
        with pytest.raises(APIKeyError):
            MistralProvider(api_key="")
    
    def test_init_with_api_key_succeeds(self):
        """Test successful initialization with API key."""
        provider = MistralProvider(api_key="test_key")
        assert provider.api_key == "test_key"
        assert provider.get_provider_name() == "mistral"


class TestMistralProvider:
    """Test Mistral AI provider."""
    
    @pytest.mark.asyncio
    async def test_generate_text_success(
        self,
        mock_rate_limiter,
        mock_cache,
        mock_cost_tracker
    ):
        """Test successful text generation."""
        provider = MistralProvider(
            api_key="test_key",
            rate_limiter=mock_rate_limiter,
            cache=mock_cache,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated text"))]
        mock_response.usage = Mock(
            total_tokens=100,
            prompt_tokens=50,
            completion_tokens=50
        )
        
        with patch.object(provider.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)):
            response = await provider.generate_text(
                prompt="Test prompt",
                model="mistral-large-latest"
            )
        
        # Verify response
        assert isinstance(response, AIResponse)
        assert response.content == "Generated text"
        assert response.model == "mistral-large-latest"
        assert response.provider == "mistral"
        assert response.tokens_used == 100
        assert response.input_tokens == 50
        assert response.output_tokens == 50
        assert not response.cached
        
        # Verify rate limiter was called
        mock_rate_limiter.acquire.assert_called_once()
        mock_rate_limiter.record_usage.assert_called_once_with(100)
        
        # Verify cost tracker was called
        mock_cost_tracker.record_call.assert_called_once()
        
        # Verify cache was checked and set
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_text_uses_cache(
        self,
        mock_rate_limiter,
        mock_cache,
        mock_cost_tracker
    ):
        """Test that cached responses are returned."""
        provider = MistralProvider(
            api_key="test_key",
            rate_limiter=mock_rate_limiter,
            cache=mock_cache,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock cached response
        mock_cache.get = AsyncMock(return_value={
            "content": "Cached text",
            "tokens_used": 100,
            "input_tokens": 50,
            "output_tokens": 50
        })
        
        response = await provider.generate_text(
            prompt="Test prompt",
            model="mistral-large-latest"
        )
        
        # Verify cached response
        assert response.content == "Cached text"
        assert response.cached is True
        assert response.cost == 0.0
        
        # Verify rate limiter was NOT called (cached response)
        mock_rate_limiter.acquire.assert_not_called()
        
        # Verify cost tracker was NOT called (cached response)
        mock_cost_tracker.record_call.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_generate_text_handles_rate_limit_error(
        self,
        mock_rate_limiter,
        mock_cache,
        mock_cost_tracker
    ):
        """Test handling of rate limit errors."""
        provider = MistralProvider(
            api_key="test_key",
            rate_limiter=mock_rate_limiter,
            cache=mock_cache,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock rate limit error
        with patch.object(
            provider.client.chat.completions,
            'create',
            new=AsyncMock(side_effect=Exception("rate_limit exceeded"))
        ):
            with pytest.raises(RateLimitError):
                await provider.generate_text(
                    prompt="Test prompt",
                    model="mistral-large-latest"
                )
        
        # Verify cost tracker recorded failure
        mock_cost_tracker.record_call.assert_called_once()
        call_args = mock_cost_tracker.record_call.call_args
        assert call_args[1]["success"] is False
    
    @pytest.mark.asyncio
    async def test_generate_text_handles_api_key_error(
        self,
        mock_rate_limiter,
        mock_cache,
        mock_cost_tracker
    ):
        """Test handling of API key errors."""
        provider = MistralProvider(
            api_key="test_key",
            rate_limiter=mock_rate_limiter,
            cache=mock_cache,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock API key error
        with patch.object(
            provider.client.chat.completions,
            'create',
            new=AsyncMock(side_effect=Exception("unauthorized api_key"))
        ):
            with pytest.raises(APIKeyError):
                await provider.generate_text(
                    prompt="Test prompt",
                    model="mistral-large-latest"
                )


class TestOpenAIProvider:
    """Test OpenAI provider."""
    
    @pytest.mark.asyncio
    async def test_generate_text_success(
        self,
        mock_rate_limiter,
        mock_cache,
        mock_cost_tracker
    ):
        """Test successful text generation with OpenAI."""
        provider = OpenAIProvider(
            api_key="test_key",
            rate_limiter=mock_rate_limiter,
            cache=mock_cache,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="OpenAI generated text"))]
        mock_response.usage = Mock(
            total_tokens=150,
            prompt_tokens=75,
            completion_tokens=75
        )
        
        with patch.object(provider.client.chat.completions, 'create', new=AsyncMock(return_value=mock_response)):
            response = await provider.generate_text(
                prompt="Test prompt",
                model="gpt-4o"
            )
        
        # Verify response
        assert isinstance(response, AIResponse)
        assert response.content == "OpenAI generated text"
        assert response.model == "gpt-4o"
        assert response.provider == "openai"
        assert response.tokens_used == 150
        assert not response.cached
        
        # Verify rate limiter was called
        mock_rate_limiter.acquire.assert_called_once()
        mock_rate_limiter.record_usage.assert_called_once_with(150)


class TestAIProviderFactory:
    """Test AI provider factory with fallback."""
    
    @pytest.mark.asyncio
    async def test_factory_uses_primary_provider(
        self,
        mock_rate_limiter,
        mock_cache,
        mock_cost_tracker
    ):
        """Test that factory uses primary provider first."""
        factory = AIProviderFactory(
            primary_provider="mistral",
            fallback_provider="openai",
            rate_limiter=mock_rate_limiter,
            cache=mock_cache,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock successful primary provider response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Primary response"))]
        mock_response.usage = Mock(
            total_tokens=100,
            prompt_tokens=50,
            completion_tokens=50
        )
        
        with patch.object(
            factory.primary.client.chat.completions,
            'create',
            new=AsyncMock(return_value=mock_response)
        ):
            response = await factory.generate_text(
                prompt="Test prompt"
            )
        
        assert response.content == "Primary response"
        assert response.provider == "mistral"
    
    @pytest.mark.asyncio
    async def test_factory_falls_back_on_primary_failure(
        self,
        mock_rate_limiter,
        mock_cache,
        mock_cost_tracker
    ):
        """Test that factory falls back to secondary provider on primary failure."""
        factory = AIProviderFactory(
            primary_provider="mistral",
            fallback_provider="openai",
            rate_limiter=mock_rate_limiter,
            cache=mock_cache,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock primary provider failure
        with patch.object(
            factory.primary.client.chat.completions,
            'create',
            new=AsyncMock(side_effect=Exception("Primary failed"))
        ):
            # Mock successful fallback provider response
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Fallback response"))]
            mock_response.usage = Mock(
                total_tokens=100,
                prompt_tokens=50,
                completion_tokens=50
            )
            
            with patch.object(
                factory.fallback.client.chat.completions,
                'create',
                new=AsyncMock(return_value=mock_response)
            ):
                response = await factory.generate_text(
                    prompt="Test prompt"
                )
        
        assert response.content == "Fallback response"
        assert response.provider == "openai"
    
    @pytest.mark.asyncio
    async def test_factory_raises_error_when_both_fail(
        self,
        mock_rate_limiter,
        mock_cache,
        mock_cost_tracker
    ):
        """Test that factory raises error when both providers fail."""
        factory = AIProviderFactory(
            primary_provider="mistral",
            fallback_provider="openai",
            rate_limiter=mock_rate_limiter,
            cache=mock_cache,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock both providers failing
        with patch.object(
            factory.primary.client.chat.completions,
            'create',
            new=AsyncMock(side_effect=Exception("Primary failed"))
        ):
            with patch.object(
                factory.fallback.client.chat.completions,
                'create',
                new=AsyncMock(side_effect=Exception("Fallback failed"))
            ):
                with pytest.raises(ContentGenerationError) as exc_info:
                    await factory.generate_text(
                        prompt="Test prompt"
                    )
                
                assert "Both providers failed" in str(exc_info.value)


class TestAIResponse:
    """Test AIResponse dataclass."""
    
    def test_ai_response_creation(self):
        """Test creating AIResponse."""
        response = AIResponse(
            content="Test content",
            model="test-model",
            provider="test-provider",
            tokens_used=100,
            input_tokens=50,
            output_tokens=50,
            cached=False,
            cost=0.05
        )
        
        assert response.content == "Test content"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.tokens_used == 100
        assert response.input_tokens == 50
        assert response.output_tokens == 50
        assert response.cached is False
        assert response.cost == 0.05
    
    def test_ai_response_defaults(self):
        """Test AIResponse with default values."""
        response = AIResponse(
            content="Test",
            model="model",
            provider="provider",
            tokens_used=100
        )
        
        assert response.input_tokens is None
        assert response.output_tokens is None
        assert response.cached is False
        assert response.cost == 0.0

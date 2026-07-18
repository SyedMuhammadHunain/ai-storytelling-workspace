"""Unit tests for image provider abstraction layer."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import base64
from PIL import Image
import io

from storytelling_workspace.core.image_provider import (
    ImageProvider,
    MistralImageProvider,
    OpenAIImageProvider,
    ImageProviderFactory,
    ImageResponse
)
from storytelling_workspace.core.exceptions import (
    APIKeyError,
    RateLimitError,
    ImageGenerationError
)
from storytelling_workspace.core.rate_limiter import RateLimiter
from storytelling_workspace.core.cost_tracker import CostTracker


@pytest.fixture
def mock_rate_limiter():
    """Create mock rate limiter."""
    limiter = Mock(spec=RateLimiter)
    limiter.acquire = AsyncMock()
    return limiter


@pytest.fixture
def mock_cost_tracker():
    """Create mock cost tracker."""
    tracker = Mock(spec=CostTracker)
    tracker.record_call = Mock(return_value=0.04)
    return tracker


@pytest.fixture
def sample_image_data():
    """Create sample image data for testing."""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


@pytest.fixture
def sample_image_b64(sample_image_data):
    """Create base64 encoded sample image."""
    return base64.b64encode(sample_image_data).decode()


class TestImageProvider:
    """Test ImageProvider base class."""
    
    def test_init_without_api_key_raises_error(self):
        """Test that initializing without API key raises error."""
        with pytest.raises(APIKeyError):
            MistralImageProvider(api_key="")
    
    def test_init_with_api_key_succeeds(self):
        """Test successful initialization with API key."""
        provider = MistralImageProvider(api_key="test_key")
        assert provider.api_key == "test_key"
        assert provider.get_provider_name() == "mistral"
    
    def test_compress_image(self, sample_image_data):
        """Test image compression."""
        provider = MistralImageProvider(api_key="test_key")
        compressed = provider._compress_image(sample_image_data, max_size_kb=50)
        
        # Compressed should be smaller or equal (or original if compression increases size)
        assert len(compressed) <= len(sample_image_data) or compressed == sample_image_data
        
        # Should still be valid image
        img = Image.open(io.BytesIO(compressed))
        assert img.size == (100, 100)


class TestMistralImageProvider:
    """Test Mistral image provider."""
    
    @pytest.mark.asyncio
    async def test_generate_image_success(
        self,
        mock_rate_limiter,
        mock_cost_tracker,
        sample_image_b64
    ):
        """Test successful image generation."""
        provider = MistralImageProvider(
            api_key="test_key",
            rate_limiter=mock_rate_limiter,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock OpenAI client response
        mock_image_data = Mock()
        mock_image_data.b64_json = sample_image_b64
        
        mock_response = Mock()
        mock_response.data = [mock_image_data]
        
        with patch.object(
            provider.client.images,
            'generate',
            new=AsyncMock(return_value=mock_response)
        ):
            response = await provider.generate_image(
                prompt="A fantasy castle",
                size="1024x1024"
            )
        
        # Verify response
        assert isinstance(response, ImageResponse)
        assert response.model == "pixtral-large-latest"
        assert response.provider == "mistral"
        assert response.size == "1024x1024"
        assert response.format == "jpeg"
        assert len(response.image_data) > 0
        
        # Verify rate limiter was called
        mock_rate_limiter.acquire.assert_called_once()
        
        # Verify cost tracker was called
        mock_cost_tracker.record_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_image_handles_rate_limit_error(
        self,
        mock_rate_limiter,
        mock_cost_tracker
    ):
        """Test handling of rate limit errors."""
        provider = MistralImageProvider(
            api_key="test_key",
            rate_limiter=mock_rate_limiter,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock rate limit error
        with patch.object(
            provider.client.images,
            'generate',
            new=AsyncMock(side_effect=Exception("rate_limit exceeded"))
        ):
            with pytest.raises(RateLimitError):
                await provider.generate_image(
                    prompt="Test prompt",
                    size="1024x1024"
                )
        
        # Verify cost tracker recorded failure (3 times due to retry)
        assert mock_cost_tracker.record_call.call_count == 3


class TestOpenAIImageProvider:
    """Test OpenAI image provider."""
    
    @pytest.mark.asyncio
    async def test_generate_image_success(
        self,
        mock_rate_limiter,
        mock_cost_tracker,
        sample_image_b64
    ):
        """Test successful image generation with OpenAI."""
        provider = OpenAIImageProvider(
            api_key="test_key",
            rate_limiter=mock_rate_limiter,
            cost_tracker=mock_cost_tracker
        )
        
        # Mock OpenAI client response
        mock_image_data = Mock()
        mock_image_data.b64_json = sample_image_b64
        
        mock_response = Mock()
        mock_response.data = [mock_image_data]
        
        with patch.object(
            provider.client.images,
            'generate',
            new=AsyncMock(return_value=mock_response)
        ):
            response = await provider.generate_image(
                prompt="A sci-fi spaceship",
                size="1024x1024",
                quality="hd"
            )
        
        # Verify response
        assert isinstance(response, ImageResponse)
        assert response.model == "dall-e-3"
        assert response.provider == "openai"
        assert response.size == "1024x1024"
        assert len(response.image_data) > 0
        
        # Verify rate limiter was called
        mock_rate_limiter.acquire.assert_called_once()


class TestImageProviderFactory:
    """Test image provider factory with fallback."""
    
    @pytest.mark.asyncio
    async def test_factory_uses_primary_provider(
        self,
        mock_rate_limiter,
        mock_cost_tracker,
        sample_image_b64
    ):
        """Test that factory uses primary provider first."""
        with patch.dict('os.environ', {'MISTRAL_API_KEY': 'test_mistral_key', 'OPENAI_API_KEY': 'test_openai_key'}):
            factory = ImageProviderFactory(
                primary_provider="mistral",
                fallback_provider="openai",
                rate_limiter=mock_rate_limiter,
                cost_tracker=mock_cost_tracker
            )
            
            # Mock successful primary provider response
            mock_image_data = Mock()
            mock_image_data.b64_json = sample_image_b64
            mock_response = Mock()
            mock_response.data = [mock_image_data]
            
            with patch.object(
                factory.primary.client.images,
                'generate',
                new=AsyncMock(return_value=mock_response)
            ):
                response = await factory.generate_image(
                    prompt="Test image"
                )
            
            assert response.provider == "mistral"
    
    @pytest.mark.asyncio
    async def test_factory_falls_back_on_primary_failure(
        self,
        mock_rate_limiter,
        mock_cost_tracker,
        sample_image_b64
    ):
        """Test that factory falls back to secondary provider on primary failure."""
        with patch.dict('os.environ', {'MISTRAL_API_KEY': 'test_mistral_key', 'OPENAI_API_KEY': 'test_openai_key'}):
            factory = ImageProviderFactory(
                primary_provider="mistral",
                fallback_provider="openai",
                rate_limiter=mock_rate_limiter,
                cost_tracker=mock_cost_tracker
            )
            
            # Mock primary provider failure
            with patch.object(
                factory.primary.client.images,
                'generate',
                new=AsyncMock(side_effect=Exception("Primary failed"))
            ):
                # Mock successful fallback provider response
                mock_image_data = Mock()
                mock_image_data.b64_json = sample_image_b64
                mock_response = Mock()
                mock_response.data = [mock_image_data]
                
                with patch.object(
                    factory.fallback.client.images,
                    'generate',
                    new=AsyncMock(return_value=mock_response)
                ):
                    response = await factory.generate_image(
                        prompt="Test image"
                    )
            
            assert response.provider == "openai"
    
    @pytest.mark.asyncio
    async def test_factory_raises_error_when_both_fail(
        self,
        mock_rate_limiter,
        mock_cost_tracker
    ):
        """Test that factory raises error when both providers fail."""
        with patch.dict('os.environ', {'MISTRAL_API_KEY': 'test_mistral_key', 'OPENAI_API_KEY': 'test_openai_key'}):
            factory = ImageProviderFactory(
                primary_provider="mistral",
                fallback_provider="openai",
                rate_limiter=mock_rate_limiter,
                cost_tracker=mock_cost_tracker
            )
            
            # Mock both providers failing
            with patch.object(
                factory.primary.client.images,
                'generate',
                new=AsyncMock(side_effect=Exception("Primary failed"))
            ):
                with patch.object(
                    factory.fallback.client.images,
                    'generate',
                    new=AsyncMock(side_effect=Exception("Fallback failed"))
                ):
                    with pytest.raises(ImageGenerationError) as exc_info:
                        await factory.generate_image(
                            prompt="Test image"
                        )
                    
                    assert "Both image providers failed" in str(exc_info.value)


class TestImageResponse:
    """Test ImageResponse dataclass."""
    
    def test_image_response_creation(self, sample_image_data):
        """Test creating ImageResponse."""
        response = ImageResponse(
            image_data=sample_image_data,
            model="test-model",
            provider="test-provider",
            size="1024x1024",
            format="png",
            cost=0.04,
            compressed_size=1024
        )
        
        assert response.image_data == sample_image_data
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.size == "1024x1024"
        assert response.format == "png"
        assert response.cost == 0.04
        assert response.compressed_size == 1024
    
    def test_image_response_defaults(self, sample_image_data):
        """Test ImageResponse with default values."""
        response = ImageResponse(
            image_data=sample_image_data,
            model="model",
            provider="provider",
            size="512x512",
            format="jpeg"
        )
        
        assert response.cost == 0.0
        assert response.compressed_size is None

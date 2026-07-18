"""Image generation provider abstraction layer using Mistral Pixtral and OpenAI DALL-E."""

import os
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from PIL import Image
import io
import base64
from openai import AsyncOpenAI

from .retry import with_retry
from .rate_limiter import RateLimiter
from .cost_tracker import CostTracker
from .exceptions import (
    ImageGenerationError,
    APIKeyError,
    RateLimitError
)

logger = logging.getLogger(__name__)


@dataclass
class ImageResponse:
    """Response from image generation provider."""
    image_data: bytes
    model: str
    provider: str
    size: str  # e.g., "1024x1024"
    format: str  # e.g., "png"
    cost: float = 0.0
    compressed_size: Optional[int] = None


class ImageProvider(ABC):
    """
    Abstract base class for image generation providers.
    
    Provides common functionality for rate limiting and cost tracking.
    Subclasses implement provider-specific image generation.
    """
    
    def __init__(
        self,
        api_key: str,
        rate_limiter: Optional[RateLimiter] = None,
        cost_tracker: Optional[CostTracker] = None
    ):
        """
        Initialize image provider.
        
        Args:
            api_key: API key for the provider
            rate_limiter: Optional rate limiter
            cost_tracker: Optional cost tracker
        """
        if not api_key:
            raise APIKeyError("API key is required")
        
        self.api_key = api_key
        self.rate_limiter = rate_limiter
        self.cost_tracker = cost_tracker
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs
    ) -> ImageResponse:
        """
        Generate image from prompt.
        
        Args:
            prompt: Image generation prompt
            size: Image size (e.g., "1024x1024", "512x512")
            quality: Image quality ("standard" or "hd")
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ImageResponse with generated image data
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name (e.g., 'mistral', 'openai')."""
        pass
    
    def _compress_image(
        self,
        image_data: bytes,
        max_size_kb: int = 500,
        quality: int = 85
    ) -> bytes:
        """
        Compress image to reduce file size.
        
        Args:
            image_data: Original image bytes
            max_size_kb: Maximum size in KB
            quality: JPEG quality (1-100)
            
        Returns:
            Compressed image bytes
        """
        try:
            # Load image
            img = Image.open(io.BytesIO(image_data))
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # Compress iteratively until under max size
            output = io.BytesIO()
            current_quality = quality
            
            while current_quality > 20:
                output.seek(0)
                output.truncate()
                img.save(output, format='JPEG', quality=current_quality, optimize=True)
                
                size_kb = len(output.getvalue()) / 1024
                if size_kb <= max_size_kb:
                    break
                
                current_quality -= 5
            
            compressed_data = output.getvalue()
            original_size = len(image_data) / 1024
            compressed_size = len(compressed_data) / 1024
            
            # Return original if compression made it larger
            if len(compressed_data) >= len(image_data):
                logger.info(
                    f"Compression would increase size ({original_size:.1f}KB → {compressed_size:.1f}KB), "
                    f"returning original"
                )
                return image_data
            
            logger.info(
                f"Image compressed: {original_size:.1f}KB → {compressed_size:.1f}KB "
                f"(quality={current_quality})"
            )
            
            return compressed_data
            
        except Exception as e:
            logger.warning(f"Image compression failed: {e}, using original")
            return image_data
    
    def _track_cost(
        self,
        model: str,
        size: str,
        success: bool = True,
        error: Optional[str] = None
    ) -> float:
        """Track image generation cost."""
        if not self.cost_tracker:
            return 0.0
        
        # Estimate tokens based on image size (rough approximation)
        tokens = 1000  # Placeholder for image generation
        
        return self.cost_tracker.record_call(
            provider=self.get_provider_name(),
            model=model,
            operation="image_generation",
            tokens_used=tokens,
            success=success,
            error=error
        )


class MistralImageProvider(ImageProvider):
    """
    Mistral Pixtral image generation provider.
    
    Uses Mistral's Pixtral Large model for image generation.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None,
        cost_tracker: Optional[CostTracker] = None
    ):
        """
        Initialize Mistral image provider.
        
        Args:
            api_key: Mistral API key (or from MISTRAL_API_KEY env var)
            rate_limiter: Optional rate limiter
            cost_tracker: Optional cost tracker
        """
        api_key = api_key or os.getenv("MISTRAL_API_KEY")
        super().__init__(api_key, rate_limiter, cost_tracker)
        
        # Initialize Mistral client (OpenAI-compatible)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.mistral.ai/v1"
        )
        
        logger.info("Initialized Mistral Pixtral image provider")
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "mistral"
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using Mistral Pixtral.
        
        Args:
            prompt: Image generation prompt
            size: Image size (1024x1024, 512x512, 1024x512)
            quality: Image quality (standard or hd)
            **kwargs: Additional parameters
            
        Returns:
            ImageResponse with generated image
        """
        # Apply rate limiting
        if self.rate_limiter:
            await self.rate_limiter.acquire(estimated_tokens=1000)
        
        try:
            # Call Mistral Pixtral API
            # Note: Pixtral Large is primarily a vision model, not image generation
            # This is a placeholder - actual implementation would use appropriate endpoint
            response = await self.client.images.generate(
                model="pixtral-large-latest",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
                response_format="b64_json",
                **kwargs
            )
            
            # Extract image data
            image_b64 = response.data[0].b64_json
            image_data = base64.b64decode(image_b64)
            
            # Compress image
            compressed_data = self._compress_image(image_data)
            
            # Track cost
            cost = self._track_cost(
                model="pixtral-large-latest",
                size=size,
                success=True
            )
            
            # Create response
            image_response = ImageResponse(
                image_data=compressed_data,
                model="pixtral-large-latest",
                provider=self.get_provider_name(),
                size=size,
                format="jpeg",
                cost=cost,
                compressed_size=len(compressed_data)
            )
            
            logger.info(
                f"Generated image with Mistral Pixtral: "
                f"{size}, {len(compressed_data)/1024:.1f}KB, ${cost:.4f}"
            )
            
            return image_response
            
        except Exception as e:
            # Track failed call
            self._track_cost(
                model="pixtral-large-latest",
                size=size,
                success=False,
                error=str(e)
            )
            
            logger.error(f"Mistral Pixtral API error: {e}")
            
            # Classify error
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"Mistral rate limit exceeded: {e}")
            elif "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                raise APIKeyError(f"Mistral API key error: {e}")
            else:
                raise ImageGenerationError(f"Mistral image generation failed: {e}")


class OpenAIImageProvider(ImageProvider):
    """
    OpenAI DALL-E image generation provider.
    
    Fallback provider when Mistral is unavailable.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None,
        cost_tracker: Optional[CostTracker] = None
    ):
        """
        Initialize OpenAI image provider.
        
        Args:
            api_key: OpenAI API key (or from OPENAI_API_KEY env var)
            rate_limiter: Optional rate limiter
            cost_tracker: Optional cost tracker
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(api_key, rate_limiter, cost_tracker)
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        logger.info("Initialized OpenAI DALL-E image provider")
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "openai"
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using OpenAI DALL-E 3.
        
        Args:
            prompt: Image generation prompt
            size: Image size (1024x1024, 1024x1792, 1792x1024)
            quality: Image quality (standard or hd)
            **kwargs: Additional parameters
            
        Returns:
            ImageResponse with generated image
        """
        # Apply rate limiting
        if self.rate_limiter:
            await self.rate_limiter.acquire(estimated_tokens=1000)
        
        try:
            # Call OpenAI DALL-E API
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
                response_format="b64_json",
                **kwargs
            )
            
            # Extract image data
            image_b64 = response.data[0].b64_json
            image_data = base64.b64decode(image_b64)
            
            # Compress image
            compressed_data = self._compress_image(image_data)
            
            # Track cost
            cost = self._track_cost(
                model="dall-e-3",
                size=size,
                success=True
            )
            
            # Create response
            image_response = ImageResponse(
                image_data=compressed_data,
                model="dall-e-3",
                provider=self.get_provider_name(),
                size=size,
                format="jpeg",
                cost=cost,
                compressed_size=len(compressed_data)
            )
            
            logger.info(
                f"Generated image with DALL-E 3: "
                f"{size}, {len(compressed_data)/1024:.1f}KB, ${cost:.4f}"
            )
            
            return image_response
            
        except Exception as e:
            # Track failed call
            self._track_cost(
                model="dall-e-3",
                size=size,
                success=False,
                error=str(e)
            )
            
            logger.error(f"OpenAI DALL-E API error: {e}")
            
            # Classify error
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"OpenAI rate limit exceeded: {e}")
            elif "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                raise APIKeyError(f"OpenAI API key error: {e}")
            else:
                raise ImageGenerationError(f"OpenAI image generation failed: {e}")


class ImageProviderFactory:
    """
    Factory for creating image providers with fallback support.
    
    Automatically falls back to OpenAI if Mistral fails.
    """
    
    def __init__(
        self,
        primary_provider: str = "mistral",
        fallback_provider: str = "openai",
        rate_limiter: Optional[RateLimiter] = None,
        cost_tracker: Optional[CostTracker] = None
    ):
        """
        Initialize image provider factory.
        
        Args:
            primary_provider: Primary provider name
            fallback_provider: Fallback provider name
            rate_limiter: Optional rate limiter
            cost_tracker: Optional cost tracker
        """
        self.primary_provider_name = primary_provider
        self.fallback_provider_name = fallback_provider
        self.rate_limiter = rate_limiter
        self.cost_tracker = cost_tracker
        
        # Initialize providers
        self.primary = self._create_provider(primary_provider)
        self.fallback = self._create_provider(fallback_provider) if fallback_provider else None
        
        logger.info(
            f"Image Provider Factory initialized: "
            f"primary={primary_provider}, fallback={fallback_provider}"
        )
    
    def _create_provider(self, provider_name: str) -> ImageProvider:
        """Create provider instance."""
        if provider_name.lower() == "mistral":
            return MistralImageProvider(
                rate_limiter=self.rate_limiter,
                cost_tracker=self.cost_tracker
            )
        elif provider_name.lower() == "openai":
            return OpenAIImageProvider(
                rate_limiter=self.rate_limiter,
                cost_tracker=self.cost_tracker
            )
        else:
            raise ValueError(f"Unknown image provider: {provider_name}")
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        **kwargs
    ) -> ImageResponse:
        """
        Generate image with automatic fallback.
        
        Args:
            prompt: Image generation prompt
            size: Image size
            quality: Image quality
            **kwargs: Additional parameters
            
        Returns:
            ImageResponse with generated image
        """
        # Try primary provider
        try:
            logger.info(f"Attempting image generation with primary provider: {self.primary_provider_name}")
            return await self.primary.generate_image(
                prompt=prompt,
                size=size,
                quality=quality,
                **kwargs
            )
        except Exception as e:
            logger.warning(
                f"Primary image provider ({self.primary_provider_name}) failed: {e}"
            )
            
            # Try fallback if available
            if self.fallback:
                logger.info(f"Falling back to: {self.fallback_provider_name}")
                try:
                    return await self.fallback.generate_image(
                        prompt=prompt,
                        size=size,
                        quality=quality,
                        **kwargs
                    )
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback image provider ({self.fallback_provider_name}) also failed: {fallback_error}"
                    )
                    raise ImageGenerationError(
                        f"Both image providers failed. Primary: {e}, Fallback: {fallback_error}"
                    )
            else:
                raise

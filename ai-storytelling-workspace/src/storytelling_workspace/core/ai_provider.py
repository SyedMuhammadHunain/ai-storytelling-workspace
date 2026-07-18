"""AI provider abstraction layer for text generation."""

import os
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from openai import AsyncOpenAI

from .retry import with_retry
from .rate_limiter import RateLimiter, RateLimitConfig
from .cache import ResponseCache
from .cost_tracker import CostTracker
from .exceptions import (
    AIProviderError,
    APIKeyError,
    ModelNotFoundError,
    ContentGenerationError,
    RateLimitError
)

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Response from AI provider."""
    content: str
    model: str
    provider: str
    tokens_used: int
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cached: bool = False
    cost: float = 0.0


class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    
    Provides common functionality for rate limiting, caching, and cost tracking.
    Subclasses implement provider-specific API calls.
    """
    
    def __init__(
        self,
        api_key: str,
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[ResponseCache] = None,
        cost_tracker: Optional[CostTracker] = None
    ):
        """
        Initialize AI provider.
        
        Args:
            api_key: API key for the provider
            rate_limiter: Optional rate limiter
            cache: Optional response cache
            cost_tracker: Optional cost tracker
        """
        if not api_key:
            raise APIKeyError("API key is required")
        
        self.api_key = api_key
        self.rate_limiter = rate_limiter
        self.cache = cache
        self.cost_tracker = cost_tracker
        
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AIResponse with generated content
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name (e.g., 'mistral', 'openai')."""
        pass
    
    async def _check_cache(
        self,
        prompt: str,
        model: str,
        parameters: Dict[str, Any]
    ) -> Optional[AIResponse]:
        """Check cache for existing response."""
        if not self.cache:
            return None
        
        cached = await self.cache.get(
            provider=self.get_provider_name(),
            model=model,
            prompt=prompt,
            parameters=parameters
        )
        
        if cached:
            logger.info(f"Cache hit for {self.get_provider_name()}/{model}")
            return AIResponse(
                content=cached["content"],
                model=model,
                provider=self.get_provider_name(),
                tokens_used=cached.get("tokens_used", 0),
                input_tokens=cached.get("input_tokens"),
                output_tokens=cached.get("output_tokens"),
                cached=True,
                cost=0.0  # No cost for cached responses
            )
        
        return None
    
    async def _save_to_cache(
        self,
        prompt: str,
        model: str,
        parameters: Dict[str, Any],
        response: AIResponse,
        ttl: int = 86400  # 24 hours
    ) -> None:
        """Save response to cache."""
        if not self.cache:
            return
        
        cache_data = {
            "content": response.content,
            "tokens_used": response.tokens_used,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens
        }
        
        await self.cache.set(
            provider=self.get_provider_name(),
            model=model,
            prompt=prompt,
            response=cache_data,
            parameters=parameters,
            ttl=ttl
        )
    
    def _track_cost(
        self,
        model: str,
        tokens_used: int,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None
    ) -> float:
        """Track API call cost."""
        if not self.cost_tracker:
            return 0.0
        
        return self.cost_tracker.record_call(
            provider=self.get_provider_name(),
            model=model,
            operation="text_generation",
            tokens_used=tokens_used,
            success=success,
            error=error,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )


class MistralProvider(AIProvider):
    """
    Mistral AI provider implementation.
    
    Uses OpenAI-compatible API for Mistral models.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[ResponseCache] = None,
        cost_tracker: Optional[CostTracker] = None
    ):
        """
        Initialize Mistral provider.
        
        Args:
            api_key: Mistral API key (or from MISTRAL_API_KEY env var)
            rate_limiter: Optional rate limiter
            cache: Optional response cache
            cost_tracker: Optional cost tracker
        """
        api_key = api_key or os.getenv("MISTRAL_API_KEY")
        super().__init__(api_key, rate_limiter, cache, cost_tracker)
        
        # Initialize Mistral client (OpenAI-compatible)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.mistral.ai/v1"
        )
        
        logger.info("Initialized Mistral AI provider")
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "mistral"
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def generate_text(
        self,
        prompt: str,
        model: str = "mistral-large-latest",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Generate text using Mistral AI.
        
        Args:
            prompt: Input prompt
            model: Mistral model name (mistral-large-latest, mistral-medium-latest, mistral-small-latest)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional parameters
            
        Returns:
            AIResponse with generated content
        """
        # Check cache first
        parameters = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        cached_response = await self._check_cache(prompt, model, parameters)
        if cached_response:
            return cached_response
        
        # Apply rate limiting
        if self.rate_limiter:
            await self.rate_limiter.acquire(estimated_tokens=max_tokens)
        
        try:
            # Call Mistral API
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            # Track cost
            cost = self._track_cost(
                model=model,
                tokens_used=tokens_used,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                success=True
            )
            
            # Update rate limiter with actual usage
            if self.rate_limiter:
                self.rate_limiter.record_usage(tokens_used)
            
            # Create response
            ai_response = AIResponse(
                content=content,
                model=model,
                provider=self.get_provider_name(),
                tokens_used=tokens_used,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached=False,
                cost=cost
            )
            
            # Cache response
            await self._save_to_cache(prompt, model, parameters, ai_response)
            
            logger.info(
                f"Generated text with Mistral {model}: "
                f"{tokens_used} tokens, ${cost:.4f}"
            )
            
            return ai_response
            
        except Exception as e:
            # Track failed call
            self._track_cost(
                model=model,
                tokens_used=0,
                success=False,
                error=str(e)
            )
            
            logger.error(f"Mistral API error: {e}")
            
            # Classify error
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"Mistral rate limit exceeded: {e}")
            elif "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                raise APIKeyError(f"Mistral API key error: {e}")
            elif "model" in str(e).lower():
                raise ModelNotFoundError(f"Mistral model not found: {e}")
            else:
                raise ContentGenerationError(f"Mistral generation failed: {e}")


class OpenAIProvider(AIProvider):
    """
    OpenAI provider implementation.
    
    Fallback provider when Mistral is unavailable.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[ResponseCache] = None,
        cost_tracker: Optional[CostTracker] = None
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (or from OPENAI_API_KEY env var)
            rate_limiter: Optional rate limiter
            cache: Optional response cache
            cost_tracker: Optional cost tracker
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__(api_key, rate_limiter, cache, cost_tracker)
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        logger.info("Initialized OpenAI provider")
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "openai"
    
    @with_retry(max_attempts=3, backoff_factor=2)
    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-4o",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Generate text using OpenAI.
        
        Args:
            prompt: Input prompt
            model: OpenAI model name (gpt-4o, gpt-3.5-turbo)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional parameters
            
        Returns:
            AIResponse with generated content
        """
        # Check cache first
        parameters = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        cached_response = await self._check_cache(prompt, model, parameters)
        if cached_response:
            return cached_response
        
        # Apply rate limiting
        if self.rate_limiter:
            await self.rate_limiter.acquire(estimated_tokens=max_tokens)
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            # Track cost
            cost = self._track_cost(
                model=model,
                tokens_used=tokens_used,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                success=True
            )
            
            # Update rate limiter with actual usage
            if self.rate_limiter:
                self.rate_limiter.record_usage(tokens_used)
            
            # Create response
            ai_response = AIResponse(
                content=content,
                model=model,
                provider=self.get_provider_name(),
                tokens_used=tokens_used,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached=False,
                cost=cost
            )
            
            # Cache response
            await self._save_to_cache(prompt, model, parameters, ai_response)
            
            logger.info(
                f"Generated text with OpenAI {model}: "
                f"{tokens_used} tokens, ${cost:.4f}"
            )
            
            return ai_response
            
        except Exception as e:
            # Track failed call
            self._track_cost(
                model=model,
                tokens_used=0,
                success=False,
                error=str(e)
            )
            
            logger.error(f"OpenAI API error: {e}")
            
            # Classify error
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"OpenAI rate limit exceeded: {e}")
            elif "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                raise APIKeyError(f"OpenAI API key error: {e}")
            elif "model" in str(e).lower():
                raise ModelNotFoundError(f"OpenAI model not found: {e}")
            else:
                raise ContentGenerationError(f"OpenAI generation failed: {e}")


class AIProviderFactory:
    """
    Factory for creating AI providers with fallback support.
    
    Automatically falls back to OpenAI if Mistral fails.
    """
    
    def __init__(
        self,
        primary_provider: str = "mistral",
        fallback_provider: str = "openai",
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[ResponseCache] = None,
        cost_tracker: Optional[CostTracker] = None
    ):
        """
        Initialize provider factory.
        
        Args:
            primary_provider: Primary provider name
            fallback_provider: Fallback provider name
            rate_limiter: Optional rate limiter
            cache: Optional response cache
            cost_tracker: Optional cost tracker
        """
        self.primary_provider_name = primary_provider
        self.fallback_provider_name = fallback_provider
        self.rate_limiter = rate_limiter
        self.cache = cache
        self.cost_tracker = cost_tracker
        
        # Initialize providers
        self.primary = self._create_provider(primary_provider)
        self.fallback = self._create_provider(fallback_provider) if fallback_provider else None
        
        logger.info(
            f"AI Provider Factory initialized: "
            f"primary={primary_provider}, fallback={fallback_provider}"
        )
    
    def _create_provider(self, provider_name: str) -> AIProvider:
        """Create provider instance."""
        if provider_name.lower() == "mistral":
            return MistralProvider(
                rate_limiter=self.rate_limiter,
                cache=self.cache,
                cost_tracker=self.cost_tracker
            )
        elif provider_name.lower() == "openai":
            return OpenAIProvider(
                rate_limiter=self.rate_limiter,
                cache=self.cache,
                cost_tracker=self.cost_tracker
            )
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Generate text with automatic fallback.
        
        Args:
            prompt: Input prompt
            model: Model name (provider-specific)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            AIResponse with generated content
        """
        # Try primary provider
        try:
            logger.info(f"Attempting generation with primary provider: {self.primary_provider_name}")
            return await self.primary.generate_text(
                prompt=prompt,
                model=model or "mistral-large-latest",
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        except Exception as e:
            logger.warning(
                f"Primary provider ({self.primary_provider_name}) failed: {e}"
            )
            
            # Try fallback if available
            if self.fallback:
                logger.info(f"Falling back to: {self.fallback_provider_name}")
                try:
                    return await self.fallback.generate_text(
                        prompt=prompt,
                        model=model or "gpt-4o",
                        max_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs
                    )
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback provider ({self.fallback_provider_name}) also failed: {fallback_error}"
                    )
                    raise ContentGenerationError(
                        f"Both providers failed. Primary: {e}, Fallback: {fallback_error}"
                    )
            else:
                raise

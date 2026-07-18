"""AI-powered agent base class using real AI providers."""

import logging
from typing import Dict, Any, Optional
from abc import abstractmethod

from .base import BaseAgent
from ..story_bible import StoryBible
from ..core.ai_provider import AIProviderFactory, AIResponse
from ..core.rate_limiter import RateLimiter, RateLimitConfig
from ..core.cache import ResponseCache, InMemoryCache
from ..core.cost_tracker import CostTracker


class AIAgent(BaseAgent):
    """
    Base class for AI-powered agents that use real AI providers.
    
    Provides common functionality for:
    - AI provider access (Mistral/OpenAI)
    - Prompt construction
    - Response parsing
    - Error handling
    """
    
    # Class-level shared resources (initialized once)
    _ai_factory: Optional[AIProviderFactory] = None
    _rate_limiter: Optional[RateLimiter] = None
    _cache: Optional[ResponseCache] = None
    _cost_tracker: Optional[CostTracker] = None
    
    def __init__(
        self,
        name: str,
        model: str = "mistral-large-latest",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize AI agent.
        
        Args:
            name: Human-readable name for this agent
            model: AI model to use (default: mistral-large-latest)
            temperature: Sampling temperature (0-1, default: 0.7)
            max_tokens: Maximum tokens to generate (default: 2000)
        """
        super().__init__(name)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize shared resources if not already done
        if AIAgent._ai_factory is None:
            self._initialize_shared_resources()
    
    @classmethod
    def _initialize_shared_resources(cls) -> None:
        """Initialize shared AI resources (called once)."""
        # Rate limiter (conservative defaults)
        rate_config = RateLimitConfig(
            requests_per_second=1.0,
            tokens_per_minute=100_000,
            burst_size=5
        )
        cls._rate_limiter = RateLimiter(rate_config)
        
        # Cache (in-memory for now, Redis in production)
        cls._cache = InMemoryCache(max_size=1000)
        
        # Cost tracker
        cls._cost_tracker = CostTracker()
        
        # AI provider factory
        cls._ai_factory = AIProviderFactory(
            primary_provider="mistral",
            fallback_provider="openai",
            rate_limiter=cls._rate_limiter,
            cache=cls._cache,
            cost_tracker=cls._cost_tracker
        )
        
        logging.info("Initialized shared AI resources for agents")
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate text using AI provider.
        
        Args:
            prompt: Input prompt
            model: Override default model
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            AIResponse with generated content
        """
        response = await self._ai_factory.generate_text(
            prompt=prompt,
            model=model or self.model,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens
        )
        
        self.log_action(
            f"Generated {response.tokens_used} tokens "
            f"(${response.cost:.4f}, cached={response.cached})"
        )
        
        return response
    
    @abstractmethod
    def build_prompt(self, bible: StoryBible, **kwargs) -> str:
        """
        Build the prompt for this agent.
        
        Args:
            bible: Story Bible with context
            **kwargs: Additional parameters for prompt construction
            
        Returns:
            Formatted prompt string
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: AIResponse, bible: StoryBible) -> Dict[str, Any]:
        """
        Parse AI response into structured data.
        
        Args:
            response: AI response to parse
            bible: Story Bible for context
            
        Returns:
            Parsed data dictionary
        """
        pass
    
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute the AI agent.
        
        Args:
            bible: Story Bible to interact with
            
        Returns:
            Execution results
        """
        self.log_start()
        
        try:
            # Build prompt
            prompt = self.build_prompt(bible)
            self.log_action(f"Built prompt ({len(prompt)} chars)")
            
            # Generate response
            response = await self.generate_text(prompt)
            
            # Parse response
            parsed_data = self.parse_response(response, bible)
            
            # Record success
            self.log_end(success=True)
            
            return {
                "success": True,
                "data": parsed_data,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "cached": response.cached,
                "provider": response.provider,
                "model": response.model
            }
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}", exc_info=True)
            self.log_end(success=False)
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    @classmethod
    def get_cost_stats(cls) -> Dict[str, Any]:
        """Get aggregated cost statistics for all agents."""
        if cls._cost_tracker:
            return cls._cost_tracker.get_stats()
        return {}
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Get cache statistics."""
        if cls._cache:
            import asyncio
            return asyncio.run(cls._cache.get_stats())
        return {}

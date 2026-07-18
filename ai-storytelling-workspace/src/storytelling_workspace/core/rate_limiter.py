"""Rate limiting for AI provider API calls."""

import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_second: float = 1.0  # Max requests per second
    tokens_per_minute: int = 500_000  # Max tokens per minute
    burst_size: int = 5  # Allow burst of requests


@dataclass
class RateLimitState:
    """State tracking for rate limiter."""
    last_request_time: float = 0.0
    tokens_used_this_minute: int = 0
    minute_start_time: float = field(default_factory=time.time)
    request_count: int = 0


class RateLimiter:
    """
    Token bucket rate limiter for AI API calls.
    
    Enforces both requests-per-second and tokens-per-minute limits.
    Uses token bucket algorithm for smooth rate limiting with burst support.
    """
    
    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter.
        
        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.state = RateLimitState()
        self._lock = asyncio.Lock()
        
    async def acquire(self, estimated_tokens: int = 1000) -> None:
        """
        Acquire permission to make an API call.
        
        Blocks until rate limit allows the request.
        
        Args:
            estimated_tokens: Estimated tokens for this request
        """
        async with self._lock:
            await self._wait_for_rate_limit()
            await self._wait_for_token_limit(estimated_tokens)
            
            # Update state
            self.state.last_request_time = time.time()
            self.state.request_count += 1
            
            logger.debug(
                f"Rate limit acquired: request #{self.state.request_count}, "
                f"tokens this minute: {self.state.tokens_used_this_minute}"
            )
    
    async def _wait_for_rate_limit(self) -> None:
        """Wait if requests-per-second limit would be exceeded."""
        current_time = time.time()
        time_since_last = current_time - self.state.last_request_time
        min_interval = 1.0 / self.config.requests_per_second
        
        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
    
    async def _wait_for_token_limit(self, estimated_tokens: int) -> None:
        """Wait if tokens-per-minute limit would be exceeded."""
        current_time = time.time()
        
        # Reset counter if minute has passed
        if current_time - self.state.minute_start_time >= 60:
            self.state.tokens_used_this_minute = 0
            self.state.minute_start_time = current_time
            logger.debug("Token counter reset for new minute")
        
        # Check if adding these tokens would exceed limit
        if self.state.tokens_used_this_minute + estimated_tokens > self.config.tokens_per_minute:
            # Calculate wait time until next minute
            time_in_minute = current_time - self.state.minute_start_time
            wait_time = 60 - time_in_minute
            
            logger.warning(
                f"Token limit would be exceeded "
                f"({self.state.tokens_used_this_minute + estimated_tokens} > "
                f"{self.config.tokens_per_minute}), waiting {wait_time:.2f}s"
            )
            
            await asyncio.sleep(wait_time)
            
            # Reset after waiting
            self.state.tokens_used_this_minute = 0
            self.state.minute_start_time = time.time()
    
    def record_usage(self, actual_tokens: int) -> None:
        """
        Record actual token usage after API call.
        
        Args:
            actual_tokens: Actual tokens used by the request
        """
        self.state.tokens_used_this_minute += actual_tokens
        
        logger.debug(
            f"Recorded {actual_tokens} tokens, "
            f"total this minute: {self.state.tokens_used_this_minute}"
        )
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get current rate limiter statistics.
        
        Returns:
            Dictionary with current stats
        """
        current_time = time.time()
        time_in_minute = current_time - self.state.minute_start_time
        
        return {
            "total_requests": self.state.request_count,
            "tokens_used_this_minute": self.state.tokens_used_this_minute,
            "tokens_remaining_this_minute": max(
                0,
                self.config.tokens_per_minute - self.state.tokens_used_this_minute
            ),
            "seconds_until_reset": max(0, 60 - time_in_minute),
            "requests_per_second_limit": self.config.requests_per_second,
            "tokens_per_minute_limit": self.config.tokens_per_minute
        }


class MultiProviderRateLimiter:
    """
    Manages rate limiters for multiple AI providers.
    
    Each provider has its own rate limits and state.
    """
    
    def __init__(self):
        """Initialize multi-provider rate limiter."""
        self._limiters: Dict[str, RateLimiter] = {}
    
    def add_provider(self, provider_name: str, config: RateLimitConfig) -> None:
        """
        Add a rate limiter for a provider.
        
        Args:
            provider_name: Name of the provider (e.g., "mistral", "openai")
            config: Rate limit configuration for this provider
        """
        self._limiters[provider_name] = RateLimiter(config)
        logger.info(f"Added rate limiter for provider: {provider_name}")
    
    async def acquire(self, provider_name: str, estimated_tokens: int = 1000) -> None:
        """
        Acquire permission for a provider.
        
        Args:
            provider_name: Name of the provider
            estimated_tokens: Estimated tokens for this request
            
        Raises:
            KeyError: If provider not found
        """
        if provider_name not in self._limiters:
            raise KeyError(f"No rate limiter configured for provider: {provider_name}")
        
        await self._limiters[provider_name].acquire(estimated_tokens)
    
    def record_usage(self, provider_name: str, actual_tokens: int) -> None:
        """
        Record usage for a provider.
        
        Args:
            provider_name: Name of the provider
            actual_tokens: Actual tokens used
        """
        if provider_name in self._limiters:
            self._limiters[provider_name].record_usage(actual_tokens)
    
    def get_stats(self, provider_name: Optional[str] = None) -> Dict[str, any]:
        """
        Get statistics for one or all providers.
        
        Args:
            provider_name: Specific provider, or None for all
            
        Returns:
            Statistics dictionary
        """
        if provider_name:
            if provider_name not in self._limiters:
                return {}
            return {provider_name: self._limiters[provider_name].get_stats()}
        
        return {
            name: limiter.get_stats()
            for name, limiter in self._limiters.items()
        }

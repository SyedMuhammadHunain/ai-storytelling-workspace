"""Response caching for AI provider calls using Redis."""

import asyncio
import hashlib
import json
import logging
from typing import Optional, Any, Dict
from datetime import timedelta
import redis.asyncio as redis

from .exceptions import CacheError

logger = logging.getLogger(__name__)


class ResponseCache:
    """
    Cache for AI provider responses using Redis.
    
    Caches responses by hashing the prompt and parameters to avoid
    redundant API calls for identical requests.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 86400  # 24 hours in seconds
    ):
        """
        Initialize response cache.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds (24h for text, 7d for images)
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._client: Optional[redis.Redis] = None
        self._connected = False
        
    async def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            self._client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False  # We'll handle encoding ourselves
            )
            # Test connection
            await self._client.ping()
            self._connected = True
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            raise CacheError(f"Redis connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._connected = False
            logger.info("Disconnected from Redis cache")
    
    def _generate_cache_key(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate cache key from request parameters.
        
        Args:
            provider: Provider name (e.g., "mistral", "openai")
            model: Model name
            prompt: Input prompt
            parameters: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Cache key string
        """
        # Create deterministic hash of request
        cache_data = {
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "parameters": parameters or {}
        }
        
        # Sort parameters for consistent hashing
        cache_json = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_json.encode()).hexdigest()
        
        # Prefix with provider and model for easier debugging
        return f"ai_cache:{provider}:{model}:{cache_hash}"
    
    async def get(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available.
        
        Args:
            provider: Provider name
            model: Model name
            prompt: Input prompt
            parameters: Additional parameters
            
        Returns:
            Cached response dict or None if not found
        """
        if not self._connected or not self._client:
            logger.warning("Cache not connected, skipping get")
            return None
        
        try:
            cache_key = self._generate_cache_key(provider, model, prompt, parameters)
            cached_data = await self._client.get(cache_key)
            
            if cached_data:
                logger.debug(f"Cache hit for key: {cache_key[:50]}...")
                return json.loads(cached_data)
            
            logger.debug(f"Cache miss for key: {cache_key[:50]}...")
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None  # Fail gracefully, don't block on cache errors
    
    async def set(
        self,
        provider: str,
        model: str,
        prompt: str,
        response: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache a response.
        
        Args:
            provider: Provider name
            model: Model name
            prompt: Input prompt
            response: Response to cache
            parameters: Additional parameters
            ttl: Time-to-live in seconds (None = use default)
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self._connected or not self._client:
            logger.warning("Cache not connected, skipping set")
            return False
        
        try:
            cache_key = self._generate_cache_key(provider, model, prompt, parameters)
            cache_value = json.dumps(response)
            
            ttl_seconds = ttl or self.default_ttl
            
            await self._client.setex(
                cache_key,
                ttl_seconds,
                cache_value
            )
            
            logger.debug(
                f"Cached response for key: {cache_key[:50]}... "
                f"(TTL: {ttl_seconds}s)"
            )
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False  # Fail gracefully
    
    async def delete(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Delete a cached response.
        
        Args:
            provider: Provider name
            model: Model name
            prompt: Input prompt
            parameters: Additional parameters
            
        Returns:
            True if deleted, False otherwise
        """
        if not self._connected or not self._client:
            return False
        
        try:
            cache_key = self._generate_cache_key(provider, model, prompt, parameters)
            deleted = await self._client.delete(cache_key)
            
            if deleted:
                logger.debug(f"Deleted cache key: {cache_key[:50]}...")
            
            return bool(deleted)
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear_provider(self, provider: str) -> int:
        """
        Clear all cached responses for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Number of keys deleted
        """
        if not self._connected or not self._client:
            return 0
        
        try:
            pattern = f"ai_cache:{provider}:*"
            keys = []
            
            # Scan for matching keys
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self._client.delete(*keys)
                logger.info(f"Cleared {deleted} cached responses for provider: {provider}")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if not self._connected or not self._client:
            return {"connected": False}
        
        try:
            info = await self._client.info("stats")
            
            # Count AI cache keys
            cache_keys = 0
            async for _ in self._client.scan_iter(match="ai_cache:*"):
                cache_keys += 1
            
            return {
                "connected": True,
                "total_cache_keys": cache_keys,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"connected": True, "error": str(e)}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100


class InMemoryCache:
    """
    Simple in-memory cache fallback when Redis is unavailable.
    
    Not recommended for production, but useful for development/testing.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize in-memory cache.
        
        Args:
            max_size: Maximum number of cached items
        """
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_order: list = []
        self._lock = asyncio.Lock()
        logger.warning("Using in-memory cache (not recommended for production)")
    
    async def connect(self) -> None:
        """No-op for in-memory cache."""
        logger.info("In-memory cache ready")
    
    async def disconnect(self) -> None:
        """No-op for in-memory cache."""
        pass
    
    def _generate_cache_key(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate cache key (same as ResponseCache)."""
        cache_data = {
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "parameters": parameters or {}
        }
        cache_json = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_json.encode()).hexdigest()
        return f"ai_cache:{provider}:{model}:{cache_hash}"
    
    async def get(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get from in-memory cache."""
        async with self._lock:
            cache_key = self._generate_cache_key(provider, model, prompt, parameters)
            
            if cache_key in self._cache:
                # Update access order (LRU)
                self._access_order.remove(cache_key)
                self._access_order.append(cache_key)
                
                logger.debug(f"In-memory cache hit: {cache_key[:50]}...")
                return self._cache[cache_key]
            
            logger.debug(f"In-memory cache miss: {cache_key[:50]}...")
            return None
    
    async def set(
        self,
        provider: str,
        model: str,
        prompt: str,
        response: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """Set in in-memory cache."""
        async with self._lock:
            cache_key = self._generate_cache_key(provider, model, prompt, parameters)
            
            # Evict oldest if at capacity
            if len(self._cache) >= self.max_size and cache_key not in self._cache:
                oldest_key = self._access_order.pop(0)
                del self._cache[oldest_key]
                logger.debug(f"Evicted oldest cache entry: {oldest_key[:50]}...")
            
            self._cache[cache_key] = response
            
            if cache_key in self._access_order:
                self._access_order.remove(cache_key)
            self._access_order.append(cache_key)
            
            logger.debug(f"Cached in memory: {cache_key[:50]}...")
            return True
    
    async def delete(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Delete from in-memory cache."""
        async with self._lock:
            cache_key = self._generate_cache_key(provider, model, prompt, parameters)
            
            if cache_key in self._cache:
                del self._cache[cache_key]
                self._access_order.remove(cache_key)
                return True
            
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get in-memory cache stats."""
        return {
            "type": "in_memory",
            "total_cache_keys": len(self._cache),
            "max_size": self.max_size,
            "usage_percent": (len(self._cache) / self.max_size) * 100
        }

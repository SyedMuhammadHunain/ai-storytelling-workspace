"""Retry logic with exponential backoff for AI provider calls."""

import asyncio
import functools
import logging
from typing import Callable, TypeVar, Any
import random

from .exceptions import RateLimitError, APIKeyError

logger = logging.getLogger(__name__)

T = TypeVar('T')


def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    max_backoff: float = 60.0,
    jitter: bool = True
):
    """
    Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff (2.0 = double each time)
        max_backoff: Maximum backoff time in seconds
        jitter: Add random jitter to backoff to prevent thundering herd
        
    Example:
        @with_retry(max_attempts=3, backoff_factor=2)
        async def call_api():
            return await client.generate(...)
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                    
                except APIKeyError:
                    # Don't retry on authentication errors
                    logger.error(f"{func.__name__}: API key error, not retrying")
                    raise
                    
                except RateLimitError as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        # Calculate backoff with exponential increase
                        backoff = min(
                            backoff_factor ** attempt,
                            max_backoff
                        )
                        
                        # Add jitter to prevent thundering herd
                        if jitter:
                            backoff = backoff * (0.5 + random.random())
                        
                        logger.warning(
                            f"{func.__name__}: Rate limit hit, "
                            f"retrying in {backoff:.2f}s (attempt {attempt + 1}/{max_attempts})"
                        )
                        await asyncio.sleep(backoff)
                    else:
                        logger.error(
                            f"{func.__name__}: Rate limit exceeded after {max_attempts} attempts"
                        )
                        raise
                        
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        backoff = min(
                            backoff_factor ** attempt,
                            max_backoff
                        )
                        
                        if jitter:
                            backoff = backoff * (0.5 + random.random())
                        
                        logger.warning(
                            f"{func.__name__}: Error occurred, "
                            f"retrying in {backoff:.2f}s (attempt {attempt + 1}/{max_attempts}): {e}"
                        )
                        await asyncio.sleep(backoff)
                    else:
                        logger.error(
                            f"{func.__name__}: Failed after {max_attempts} attempts: {e}"
                        )
                        raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


async def retry_with_backoff(
    func: Callable[..., T],
    *args: Any,
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    max_backoff: float = 60.0,
    **kwargs: Any
) -> T:
    """
    Retry an async function with exponential backoff.
    
    Alternative to decorator for one-off retries.
    
    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_attempts: Maximum retry attempts
        backoff_factor: Exponential backoff multiplier
        max_backoff: Maximum backoff time in seconds
        **kwargs: Keyword arguments for func
        
    Returns:
        Result from successful function call
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
            
        except APIKeyError:
            logger.error(f"API key error, not retrying")
            raise
            
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                backoff = min(
                    backoff_factor ** attempt,
                    max_backoff
                )
                backoff = backoff * (0.5 + random.random())
                
                logger.warning(
                    f"Retry attempt {attempt + 1}/{max_attempts} "
                    f"after {backoff:.2f}s: {e}"
                )
                await asyncio.sleep(backoff)
            else:
                logger.error(f"Failed after {max_attempts} attempts: {e}")
                raise
    
    if last_exception:
        raise last_exception

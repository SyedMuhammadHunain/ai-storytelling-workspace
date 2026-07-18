"""Custom exceptions for AI Storytelling Workspace."""


class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    pass


class RateLimitError(AIProviderError):
    """Raised when rate limit is exceeded."""
    pass


class APIKeyError(AIProviderError):
    """Raised when API key is invalid or missing."""
    pass


class ModelNotFoundError(AIProviderError):
    """Raised when requested model is not available."""
    pass


class ContentGenerationError(AIProviderError):
    """Raised when content generation fails."""
    pass


class ImageGenerationError(AIProviderError):
    """Raised when image generation fails."""
    pass


class CacheError(Exception):
    """Base exception for cache errors."""
    pass


class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass


class CheckpointError(WorkflowError):
    """Raised when checkpoint operations fail."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

"""Base agent classes for the storytelling workspace."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from ..story_bible import StoryBible
from ..core.ai_provider import AIProviderFactory, AIResponse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the storytelling workspace.
    
    All agents must implement the execute() method and interact with
    the Story Bible for reading and writing state.
    """
    
    def __init__(self, name: str):
        """
        Initialize the agent.
        
        Args:
            name: Human-readable name for this agent
        """
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")
        
    @abstractmethod
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute the agent's task.
        
        Args:
            bible: The Story Bible to read from and write to
            
        Returns:
            Dictionary containing execution results and any outputs
        """
        pass
        
    def log_start(self) -> None:
        """Log the start of agent execution."""
        self.logger.info(f"Starting execution: {self.name}")
        
    def log_end(self, success: bool = True) -> None:
        """Log the end of agent execution."""
        status = "completed successfully" if success else "failed"
        self.logger.info(f"Execution {status}: {self.name}")
        
    def log_action(self, action: str) -> None:
        """Log a specific action taken by the agent."""
        self.logger.info(f"[{self.name}] {action}")
        
    def record_changes(self, bible: StoryBible, changes: Dict[str, Any], summary: str) -> None:
        """
        Record changes made to the Story Bible.
        
        Args:
            bible: The Story Bible being modified
            changes: Dictionary describing what changed
            summary: Human-readable summary of changes
        """
        bible.record_delta(
            agent_name=self.name,
            changes=changes,
            summary=summary
        )
        self.log_action(f"Recorded changes: {summary}")


class AIAgent(BaseAgent):
    """
    Base class for agents that use AI providers for content generation.
    
    Provides common functionality for calling AI APIs with proper error handling,
    logging, and cost tracking.
    """
    
    def __init__(
        self,
        name: str,
        ai_provider: Optional[AIProviderFactory] = None,
        default_model: str = "mistral-large-latest",
        default_temperature: float = 0.7,
        default_max_tokens: int = 2000
    ):
        """
        Initialize the AI agent.
        
        Args:
            name: Human-readable name for this agent
            ai_provider: AI provider factory (creates one if not provided)
            default_model: Default model to use for generation
            default_temperature: Default temperature for generation
            default_max_tokens: Default max tokens for generation
        """
        super().__init__(name)
        
        # Initialize AI provider if not provided
        if ai_provider is None:
            from ..core.rate_limiter import RateLimiter, RateLimitConfig
            from ..core.cache import ResponseCache
            from ..core.cost_tracker import CostTracker
            
            # Create default components
            rate_limiter = RateLimiter(RateLimitConfig(
                requests_per_second=1.0,
                tokens_per_minute=500000
            ))
            cache = ResponseCache()
            cost_tracker = CostTracker()
            
            ai_provider = AIProviderFactory(
                primary_provider="mistral",
                fallback_provider="openai",
                rate_limiter=rate_limiter,
                cache=cache,
                cost_tracker=cost_tracker
            )
        
        self.ai_provider = ai_provider
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate text using AI provider.
        
        Args:
            prompt: Input prompt
            model: Model name (uses default if not provided)
            temperature: Sampling temperature (uses default if not provided)
            max_tokens: Maximum tokens (uses default if not provided)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AIResponse with generated content
        """
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        self.log_action(f"Generating text with {model} (temp={temperature}, max_tokens={max_tokens})")
        
        try:
            response = await self.ai_provider.generate_text(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            self.log_action(
                f"Generated {response.tokens_used} tokens "
                f"(${response.cost:.4f}) "
                f"{'[CACHED]' if response.cached else ''}"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"AI generation failed: {e}")
            raise
    
    def format_prompt(self, template: str, **kwargs) -> str:
        """
        Format a prompt template with variables.
        
        Args:
            template: Prompt template with {placeholders}
            **kwargs: Values to fill in the template
            
        Returns:
            Formatted prompt
        """
        return template.format(**kwargs)


class MockAgent(BaseAgent):
    """
    Base class for mock agents that generate simple placeholder outputs.
    
    Mock agents are used to validate the orchestration pattern without
    requiring real AI integration.
    """
    
    def __init__(self, name: str, mock_output: Optional[str] = None):
        """
        Initialize the mock agent.
        
        Args:
            name: Human-readable name for this agent
            mock_output: Optional predefined output string
        """
        super().__init__(name)
        self.mock_output = mock_output or f"Mock output from {name}"
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute the mock agent.
        
        Args:
            bible: The Story Bible to interact with
            
        Returns:
            Dictionary with mock execution results
        """
        self.log_start()
        
        # Generate mock output
        result = {
            "success": True,
            "output": self.mock_output,
            "timestamp": datetime.now().isoformat()
        }
        
        # Record that this agent ran
        self.record_changes(
            bible,
            changes={"executed": True},
            summary=f"{self.name} executed with mock output"
        )
        
        self.log_end(success=True)
        return result
        
    def generate_mock_text(self, template: str, **kwargs) -> str:
        """
        Generate mock text from a template.
        
        Args:
            template: Template string with {placeholders}
            **kwargs: Values to fill in the template
            
        Returns:
            Formatted mock text
        """
        return template.format(**kwargs)
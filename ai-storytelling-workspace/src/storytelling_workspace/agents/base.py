"""Base agent classes for the storytelling workspace."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from ..story_bible import StoryBible


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

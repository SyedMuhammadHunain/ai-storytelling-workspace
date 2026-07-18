"""Intake Agent - Captures initial book parameters."""

from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible
from ..models import BookBrief


class IntakeAgent(MockAgent):
    """
    Intake Agent captures user input for the book project.
    
    In the MVP, this uses mock data. In production, it would prompt
    the user for genre, premise, target length, tone, etc.
    """
    
    def __init__(self):
        """Initialize the Intake Agent."""
        super().__init__(name="Intake Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute intake - capture book parameters.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # In MVP, use mock data
        # In production, this would prompt user for input
        brief = self._create_mock_brief()
        
        # Update Story Bible
        bible.brief = brief
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "brief": {
                    "genre": brief.genre,
                    "premise": brief.premise,
                    "target_length": brief.target_length
                }
            },
            summary=f"Created book brief: {brief.genre} novel, {brief.target_length} words"
        )
        
        self.log_action(f"Captured book parameters: {brief.genre}, {brief.target_length} words")
        self.log_end(success=True)
        
        return {
            "success": True,
            "brief": brief.to_dict()
        }
        
    def _create_mock_brief(self) -> BookBrief:
        """Create mock book brief for MVP."""
        return BookBrief(
            genre="Fantasy",
            premise="A young hero discovers they have magical powers and must save their kingdom from an ancient evil",
            target_length=80000,
            tone="Epic and adventurous with moments of humor",
            audience="Young Adult",
            pov="Third person limited"
        )

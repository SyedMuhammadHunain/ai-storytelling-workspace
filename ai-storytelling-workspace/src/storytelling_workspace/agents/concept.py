"""Concept Agent - Expands brief into full concept."""

from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible
from ..models import Concept


class ConceptAgent(MockAgent):
    """
    Concept Agent expands the book brief into a full concept.
    
    Generates logline, premise, central conflict, and theme.
    """
    
    def __init__(self):
        """Initialize the Concept Agent."""
        super().__init__(name="Concept Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute concept development.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Generate concept from brief
        concept = self._create_mock_concept(bible.brief.genre, bible.brief.premise)
        
        # Update Story Bible
        bible.concept = concept
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "concept": {
                    "logline": concept.logline,
                    "theme": concept.theme
                }
            },
            summary=f"Developed concept with theme: {concept.theme}"
        )
        
        self.log_action(f"Created concept: {concept.logline}")
        self.log_end(success=True)
        
        return {
            "success": True,
            "concept": concept.to_dict()
        }
        
    def _create_mock_concept(self, genre: str, premise: str) -> Concept:
        """Create mock concept for MVP."""
        return Concept(
            logline="When a young apprentice discovers ancient magic, they must master their powers to defeat a rising darkness threatening the kingdom.",
            premise=premise,
            central_conflict="The protagonist must overcome their self-doubt and inexperience while facing a powerful enemy who seeks to destroy everything they love.",
            theme="Courage in the face of overwhelming odds; the power of believing in oneself"
        )

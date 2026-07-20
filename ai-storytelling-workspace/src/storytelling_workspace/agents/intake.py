"""Intake Agent - Captures initial book parameters."""

import asyncio
from typing import Dict, Any

from .base import AIAgent
from ..story_bible import StoryBible
from ..models import BookBrief
from ..utils.prompts import PromptTemplates


class IntakeAgent(AIAgent):
    """
    Intake Agent captures and refines user input for the book project.
    
    Uses AI to enhance and validate the initial book brief.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Intake Agent."""
        super().__init__(
            name="Intake Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.7,
            default_max_tokens=1000
        )
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute intake - capture and refine book parameters.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # For MVP, use mock data as input
        # In production, this would come from user input
        initial_brief = self._get_initial_input()
        
        # Use AI to refine and enhance the brief
        enhanced_brief = await self._enhance_brief(initial_brief)
        
        # Update Story Bible
        bible.brief = enhanced_brief
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "brief": {
                    "genre": enhanced_brief.genre,
                    "premise": enhanced_brief.premise,
                    "target_length": enhanced_brief.target_length,
                    "tone": enhanced_brief.tone
                }
            },
            summary=f"Created book brief: {enhanced_brief.genre} novel, {enhanced_brief.target_length} words"
        )
        
        self.log_action(f"Captured book parameters: {enhanced_brief.genre}, {enhanced_brief.target_length} words")
        self.log_end(success=True)
        
        return {
            "success": True,
            "brief": enhanced_brief.to_dict()
        }
    
    def _get_initial_input(self) -> Dict[str, Any]:
        """
        Get initial input from user.
        
        In MVP, returns mock data.
        In production, would prompt user for input.
        
        Returns:
            Dictionary with initial book parameters
        """
        return {
            "genre": "Fantasy",
            "premise": "A young hero discovers they have magical powers and must save their kingdom from an ancient evil",
            "target_length": 80000,
            "tone": "Epic and adventurous",
            "audience": "Young Adult",
            "pov": "Third person limited"
        }
    
    async def _enhance_brief(self, initial_input: Dict[str, Any]) -> BookBrief:
        """
        Use AI to enhance and validate the book brief.
        
        Args:
            initial_input: Initial user input
            
        Returns:
            Enhanced BookBrief
        """
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.INTAKE_BRIEF,
            genre=initial_input["genre"],
            premise=initial_input["premise"],
            target_word_count=initial_input["target_length"],
            target_audience=initial_input.get("audience", "General"),
            tone=initial_input["tone"]
        )
        
        # Generate enhanced brief with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse response and create BookBrief
        # For now, use the original input with AI-enhanced premise
        # In production, would parse AI response more thoroughly
        enhanced_premise = self._extract_premise(response.content) or initial_input["premise"]
        
        return BookBrief(
            genre=initial_input["genre"],
            premise=enhanced_premise,
            target_length=initial_input["target_length"],
            tone=initial_input["tone"],
            audience=initial_input.get("audience", "General"),
            pov=initial_input.get("pov", "Third person")
        )
    
    def _extract_premise(self, ai_response: str) -> str:
        """
        Extract refined premise from AI response.
        
        Args:
            ai_response: AI response text
            
        Returns:
            Extracted premise or empty string
        """
        # Look for premise in response
        lines = ai_response.strip().split('\n')
        
        for i, line in enumerate(lines):
            if 'premise' in line.lower() and ':' in line:
                # Get content after colon
                premise = line.split(':', 1)[1].strip()
                if premise:
                    return premise
                # Check next line if premise is on separate line
                if i + 1 < len(lines):
                    return lines[i + 1].strip()
        
        # Fallback: return first substantial paragraph
        for line in lines:
            line = line.strip()
            if len(line) > 50 and not line.startswith('#'):
                return line
        
        return ""
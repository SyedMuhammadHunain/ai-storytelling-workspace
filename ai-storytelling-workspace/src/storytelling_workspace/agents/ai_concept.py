"""AI-powered Concept Agent using real AI providers."""

import json
from typing import Dict, Any

from .ai_agent import AIAgent
from ..story_bible import StoryBible
from ..models import Concept
from ..core.ai_provider import AIResponse
from ..utils.prompts import build_concept_prompt


class AIConceptAgent(AIAgent):
    """
    AI-powered Concept Agent that expands brief into full concept.
    
    Uses real AI to generate:
    - Compelling logline
    - Central conflict
    - Theme
    """
    
    def __init__(self):
        """Initialize AI Concept Agent."""
        super().__init__(
            name="AI Concept Agent",
            model="mistral-large-latest",
            temperature=0.7,
            max_tokens=1000
        )
    
    def build_prompt(self, bible: StoryBible, **kwargs) -> str:
        """
        Build prompt for concept generation.
        
        Args:
            bible: Story Bible with brief
            **kwargs: Additional parameters
            
        Returns:
            Formatted prompt
        """
        return build_concept_prompt(
            genre=bible.brief.genre,
            premise=bible.brief.premise,
            tone=bible.brief.tone
        )
    
    def parse_response(self, response: AIResponse, bible: StoryBible) -> Dict[str, Any]:
        """
        Parse AI response into Concept model.
        
        Args:
            response: AI response
            bible: Story Bible
            
        Returns:
            Parsed concept data
        """
        try:
            # Try to parse as JSON
            content = response.content.strip()
            
            # Extract JSON if wrapped in markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            data = json.loads(content)
            
            # Create Concept model
            concept = Concept(
                logline=data.get("logline", ""),
                premise=bible.brief.premise,
                central_conflict=data.get("central_conflict", ""),
                theme=data.get("theme", "")
            )
            
            # Update Story Bible
            bible.concept = concept
            
            # Record changes
            self.record_changes(
                bible,
                changes={
                    "concept": {
                        "logline": concept.logline,
                        "theme": concept.theme,
                        "central_conflict": concept.central_conflict
                    }
                },
                summary=f"AI-generated concept with theme: {concept.theme}"
            )
            
            return {
                "concept": concept.to_dict(),
                "logline": concept.logline,
                "theme": concept.theme,
                "central_conflict": concept.central_conflict
            }
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            
            # Fallback: extract text manually
            content = response.content
            
            # Simple extraction (not ideal, but works as fallback)
            concept = Concept(
                logline=self._extract_field(content, "logline") or "Generated concept",
                premise=bible.brief.premise,
                central_conflict=self._extract_field(content, "central_conflict") or "Conflict to be determined",
                theme=self._extract_field(content, "theme") or "Theme to be determined"
            )
            
            bible.concept = concept
            
            self.record_changes(
                bible,
                changes={"concept": concept.to_dict()},
                summary="AI-generated concept (fallback parsing)"
            )
            
            return {
                "concept": concept.to_dict(),
                "warning": "Used fallback parsing"
            }
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """
        Extract field value from text (fallback method).
        
        Args:
            text: Text to search
            field_name: Field to extract
            
        Returns:
            Extracted value or empty string
        """
        # Look for patterns like "logline": "..." or **Logline:** ...
        patterns = [
            f'"{field_name}": "',
            f'"{field_name}":"',
            f'**{field_name.title()}:**',
            f'{field_name.title()}:',
        ]
        
        for pattern in patterns:
            if pattern in text:
                start = text.find(pattern) + len(pattern)
                # Find end (quote or newline)
                end = text.find('"', start) if '"' in pattern else text.find('\n', start)
                if end > start:
                    return text[start:end].strip()
        
        return ""

"""AI-powered Character Agent using real AI providers."""

import json
from typing import Dict, Any, List

from .ai_agent import AIAgent
from ..story_bible import StoryBible
from ..models import Character
from ..core.ai_provider import AIResponse
from ..utils.prompts import build_character_prompt


class AICharacterAgent(AIAgent):
    """
    AI-powered Character Agent that creates detailed character profiles.
    
    Uses real AI to generate:
    - Protagonist, antagonist, and supporting characters
    - Goals, flaws, arcs, and voice signatures
    - Physical descriptions and backstories
    """
    
    def __init__(self):
        """Initialize AI Character Agent."""
        super().__init__(
            name="AI Character Agent",
            model="mistral-large-latest",
            temperature=0.8,  # Higher temperature for more creative characters
            max_tokens=2000
        )
    
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute character creation for all main roles.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        try:
            characters_created = []
            total_cost = 0.0
            total_tokens = 0
            
            # Create protagonist
            protagonist = await self._create_character(bible, "protagonist")
            if protagonist:
                bible.add_character(protagonist)
                characters_created.append(protagonist)
            
            # Create antagonist
            antagonist = await self._create_character(bible, "antagonist")
            if antagonist:
                bible.add_character(antagonist)
                characters_created.append(antagonist)
            
            # Create 1-2 supporting characters
            for i in range(2):
                supporting = await self._create_character(bible, "supporting")
                if supporting:
                    bible.add_character(supporting)
                    characters_created.append(supporting)
            
            # Record changes
            self.record_changes(
                bible,
                changes={
                    "characters": [char.name for char in characters_created]
                },
                summary=f"AI-generated {len(characters_created)} characters: {', '.join(char.name for char in characters_created)}"
            )
            
            self.log_action(f"Created {len(characters_created)} character profiles")
            self.log_end(success=True)
            
            return {
                "success": True,
                "characters_count": len(characters_created),
                "characters": [char.to_dict() for char in characters_created]
            }
            
        except Exception as e:
            self.logger.error(f"Character creation failed: {e}", exc_info=True)
            self.log_end(success=False)
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _create_character(self, bible: StoryBible, role: str) -> Character:
        """
        Create a single character.
        
        Args:
            bible: Story Bible with context
            role: Character role (protagonist, antagonist, supporting)
            
        Returns:
            Character model
        """
        # Build prompt
        prompt = self.build_prompt(bible, role=role)
        
        # Generate response
        response = await self.generate_text(prompt)
        
        # Parse response
        character_data = self._parse_character_response(response)
        
        # Create Character model
        character = Character(
            name=character_data.get("name", f"Character ({role})"),
            role=role,
            goals=character_data.get("goals", []),
            flaws=character_data.get("flaws", []),
            arc=character_data.get("arc", ""),
            voice_signature=character_data.get("voice_signature", ""),
            physical_description=character_data.get("physical_description", ""),
            backstory=character_data.get("backstory", "")
        )
        
        self.log_action(f"Created {role}: {character.name}")
        
        return character
    
    def build_prompt(self, bible: StoryBible, **kwargs) -> str:
        """
        Build prompt for character generation.
        
        Args:
            bible: Story Bible with concept
            **kwargs: Must include 'role' parameter
            
        Returns:
            Formatted prompt
        """
        role = kwargs.get("role", "protagonist")
        
        return build_character_prompt(
            concept_logline=bible.concept.logline if bible.concept else "A compelling story",
            theme=bible.concept.theme if bible.concept else "Universal themes",
            genre=bible.brief.genre,
            character_role=role
        )
    
    def parse_response(self, response: AIResponse, bible: StoryBible) -> Dict[str, Any]:
        """
        Parse AI response (not used directly, see _parse_character_response).
        
        Args:
            response: AI response
            bible: Story Bible
            
        Returns:
            Parsed data
        """
        return self._parse_character_response(response)
    
    def _parse_character_response(self, response: AIResponse) -> Dict[str, Any]:
        """
        Parse character response into structured data.
        
        Args:
            response: AI response
            
        Returns:
            Character data dictionary
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
            
            # Ensure lists are lists
            if "goals" in data and isinstance(data["goals"], str):
                data["goals"] = [data["goals"]]
            if "flaws" in data and isinstance(data["flaws"], str):
                data["flaws"] = [data["flaws"]]
            
            return data
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            
            # Fallback: extract text manually
            content = response.content
            
            return {
                "name": self._extract_field(content, "name") or "Character",
                "physical_description": self._extract_field(content, "physical_description") or "",
                "backstory": self._extract_field(content, "backstory") or "",
                "goals": [self._extract_field(content, "goals") or "Achieve their purpose"],
                "flaws": [self._extract_field(content, "flaws") or "To be determined"],
                "arc": self._extract_field(content, "arc") or "",
                "voice_signature": self._extract_field(content, "voice_signature") or ""
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
        patterns = [
            f'"{field_name}": "',
            f'"{field_name}":"',
            f'**{field_name.replace("_", " ").title()}:**',
            f'{field_name.replace("_", " ").title()}:',
        ]
        
        for pattern in patterns:
            if pattern in text:
                start = text.find(pattern) + len(pattern)
                end = text.find('"', start) if '"' in pattern else text.find('\n', start)
                if end > start:
                    return text[start:end].strip()
        
        return ""

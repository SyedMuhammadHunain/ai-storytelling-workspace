"""Character Agent - Creates character profiles."""

import asyncio
import json
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..models import Character
from ..utils.prompts import PromptTemplates


class CharacterAgent(AIAgent):
    """
    Character Agent creates detailed character profiles.
    
    Uses AI to generate protagonist, antagonist, and supporting characters
    with goals, flaws, arcs, and voice signatures.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Character Agent."""
        super().__init__(
            name="Character Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.8,  # Higher temperature for creative character development
            default_max_tokens=3000
        )
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute character creation.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Generate characters with AI
        characters = await self._generate_characters(bible)
        
        # Add characters to Story Bible
        for character in characters:
            bible.add_character(character)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "characters": [char.name for char in characters]
            },
            summary=f"Created {len(characters)} characters: {', '.join(char.name for char in characters)}"
        )
        
        self.log_action(f"Created {len(characters)} character profiles")
        self.log_end(success=True)
        
        return {
            "success": True,
            "characters_count": len(characters),
            "characters": [char.to_dict() for char in characters]
        }
    
    async def _generate_characters(self, bible: StoryBible, num_characters: int = 3) -> List[Character]:
        """
        Generate characters using AI.
        
        Args:
            bible: Story Bible with story context
            num_characters: Number of characters to generate
            
        Returns:
            List of Character objects
        """
        # Prepare world summary
        world_summary = self._prepare_world_summary(bible)
        
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.CHARACTER_DEVELOPMENT,
            genre=bible.brief.genre,
            logline=bible.concept.logline,
            central_conflict=bible.concept.central_conflict,
            world_summary=world_summary,
            num_characters=num_characters
        )
        
        # Generate characters with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.8,
            max_tokens=3000
        )
        
        # Parse AI response into Character objects
        characters = self._parse_characters_response(response.content)
        
        # Ensure we have at least protagonist and antagonist
        if not characters:
            characters = self._create_default_characters()
        
        return characters
    
    def _prepare_world_summary(self, bible: StoryBible) -> str:
        """
        Prepare a summary of the world for character context.
        
        Args:
            bible: Story Bible
            
        Returns:
            World summary string
        """
        if not bible.world_rules:
            return "World details to be determined"
        
        summary_parts = []
        
        if bible.world_rules.magic_system:
            summary_parts.append(f"Magic: {bible.world_rules.magic_system}")
        
        if bible.world_rules.social_structure:
            summary_parts.append(f"Society: {bible.world_rules.social_structure}")
        
        if bible.locations:
            locations = ", ".join([loc.name for loc in bible.locations[:3]])
            summary_parts.append(f"Key locations: {locations}")
        
        return "; ".join(summary_parts) if summary_parts else "World details to be determined"
    
    def _parse_characters_response(self, ai_response: str) -> List[Character]:
        """
        Parse AI response into Character objects.
        
        Args:
            ai_response: Raw AI response text
            
        Returns:
            List of Character objects
        """
        characters = []
        lines = ai_response.strip().split('\n')
        
        current_character = {}
        current_field = None
        current_list = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Detect character boundaries
            if 'character' in line.lower() and (':' in line or line.endswith(':')):
                # Save previous character
                if current_character and 'name' in current_character:
                    characters.append(self._create_character_from_dict(current_character))
                current_character = {}
                current_field = None
                current_list = []
                continue
            
            # Detect fields
            lower_line = line.lower()
            if 'name:' in lower_line:
                current_field = 'name'
                current_character['name'] = line.split(':', 1)[1].strip()
            elif 'role:' in lower_line:
                current_field = 'role'
                current_character['role'] = line.split(':', 1)[1].strip().lower()
            elif 'physical' in lower_line and 'description' in lower_line:
                current_field = 'physical_description'
                if ':' in line:
                    current_character['physical_description'] = line.split(':', 1)[1].strip()
            elif 'personality' in lower_line or 'traits' in lower_line:
                current_field = 'personality'
                if ':' in line:
                    current_character['personality'] = line.split(':', 1)[1].strip()
            elif 'background' in lower_line or 'backstory' in lower_line:
                current_field = 'backstory'
                if ':' in line:
                    current_character['backstory'] = line.split(':', 1)[1].strip()
            elif 'goal' in lower_line:
                current_field = 'goals'
                current_list = []
                if ':' in line and line.split(':', 1)[1].strip():
                    current_list.append(line.split(':', 1)[1].strip())
            elif 'flaw' in lower_line:
                current_field = 'flaws'
                current_list = []
                if ':' in line and line.split(':', 1)[1].strip():
                    current_list.append(line.split(':', 1)[1].strip())
            elif 'arc' in lower_line:
                current_field = 'arc'
                if ':' in line:
                    current_character['arc'] = line.split(':', 1)[1].strip()
            elif 'voice' in lower_line:
                current_field = 'voice_signature'
                if ':' in line:
                    current_character['voice_signature'] = line.split(':', 1)[1].strip()
            elif line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                # List item
                item = line.lstrip('-•*123456789. ')
                if current_field == 'goals':
                    current_list.append(item)
                elif current_field == 'flaws':
                    current_list.append(item)
            elif current_field and line:
                # Continuation of previous field
                if current_field in ['goals', 'flaws']:
                    if current_list:
                        current_list[-1] += ' ' + line
                    else:
                        current_list.append(line)
                elif current_field in current_character:
                    current_character[current_field] += ' ' + line
            
            # Save lists
            if current_field == 'goals' and current_list:
                current_character['goals'] = current_list
            elif current_field == 'flaws' and current_list:
                current_character['flaws'] = current_list
        
        # Save last character
        if current_character and 'name' in current_character:
            characters.append(self._create_character_from_dict(current_character))
        
        return characters
    
    def _create_character_from_dict(self, char_dict: Dict[str, Any]) -> Character:
        """
        Create Character object from parsed dictionary.
        
        Args:
            char_dict: Dictionary with character data
            
        Returns:
            Character object
        """
        return Character(
            name=char_dict.get('name', 'Unnamed Character'),
            role=char_dict.get('role', 'supporting'),
            goals=char_dict.get('goals', ['Goals to be determined']),
            flaws=char_dict.get('flaws', ['Flaws to be determined']),
            arc=char_dict.get('arc', 'Character arc to be determined'),
            voice_signature=char_dict.get('voice_signature', 'Voice to be determined'),
            physical_description=char_dict.get('physical_description', 'Description to be added'),
            backstory=char_dict.get('backstory', 'Backstory to be developed')
        )
    
    def _create_default_characters(self) -> List[Character]:
        """Create default characters as fallback."""
        return [
            Character(
                name="The Protagonist",
                role="protagonist",
                goals=["Achieve their goal", "Overcome obstacles"],
                flaws=["Self-doubt", "Inexperience"],
                arc="Growth from uncertainty to confidence",
                voice_signature="Determined and earnest",
                physical_description="To be determined",
                backstory="To be developed"
            ),
            Character(
                name="The Antagonist",
                role="antagonist",
                goals=["Oppose the protagonist", "Achieve their own goals"],
                flaws=["Arrogance", "Obsession"],
                arc="Descent into darkness",
                voice_signature="Commanding and cold",
                physical_description="To be determined",
                backstory="To be developed"
            )
        ]
"""Character Agent - Creates character profiles."""

from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible
from ..models import Character


class CharacterAgent(MockAgent):
    """
    Character Agent creates detailed character profiles.
    
    Generates protagonist, antagonist, and supporting characters
    with goals, flaws, arcs, and voice signatures.
    """
    
    def __init__(self):
        """Initialize the Character Agent."""
        super().__init__(name="Character Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute character creation.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Create main characters
        characters = self._create_mock_characters()
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
        
    def _create_mock_characters(self) -> list:
        """Create mock character profiles for MVP."""
        return [
            Character(
                name="Aria Stormwind",
                role="protagonist",
                goals=[
                    "Master her newfound magical abilities",
                    "Protect her kingdom from the rising darkness",
                    "Prove herself worthy despite her humble origins"
                ],
                flaws=[
                    "Self-doubt and imposter syndrome",
                    "Tendency to act impulsively when emotional",
                    "Struggles to trust others with her secrets"
                ],
                arc="From uncertain apprentice to confident hero who learns that true strength comes from accepting help and believing in herself",
                voice_signature="Direct and earnest, with occasional sarcasm when nervous. Uses simple, practical language.",
                physical_description="17 years old, dark curly hair, green eyes, average height, often wears practical traveling clothes",
                backstory="Orphaned as a child, raised by a village blacksmith. Discovered her magic accidentally during a village crisis."
            ),
            Character(
                name="Lord Malachar",
                role="antagonist",
                goals=[
                    "Break the ancient seals and reclaim dark magic",
                    "Overthrow the current kingdom and establish a new order",
                    "Prove that power, not virtue, determines who should rule"
                ],
                flaws=[
                    "Arrogance and overconfidence in his abilities",
                    "Inability to understand or value human connection",
                    "Obsession with power blinds him to alternatives"
                ],
                arc="Descends further into darkness as his quest for power consumes him, ultimately becoming the very evil he once sought to control",
                voice_signature="Eloquent and commanding, speaks in formal, archaic patterns. Uses metaphors of darkness and power.",
                physical_description="Tall, gaunt figure with pale skin and dark robes. Eyes that seem to absorb light.",
                backstory="Former royal advisor who was exiled for practicing forbidden magic. Seeks revenge and vindication."
            ),
            Character(
                name="Master Eldrin",
                role="supporting",
                goals=[
                    "Train Aria to control her powers",
                    "Protect the kingdom's magical secrets",
                    "Atone for past failures"
                ],
                flaws=[
                    "Haunted by past mistakes",
                    "Overly cautious and secretive",
                    "Struggles to express emotions"
                ],
                arc="Learns to trust his student and overcome his fear of failure, ultimately sacrificing himself to give Aria the chance to succeed",
                voice_signature="Measured and thoughtful, speaks in teaching parables. Often cryptic but well-meaning.",
                physical_description="Elderly mage with white beard, kind eyes, and weathered hands. Wears traditional mage robes.",
                backstory="Once the kingdom's greatest mage, failed to stop a previous dark threat. Now seeks redemption through teaching."
            )
        ]

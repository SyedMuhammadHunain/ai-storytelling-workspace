"""Worldbuilding Agent - Creates world rules and settings."""

from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible
from ..models import WorldRules, Location, TimelineEvent


class WorldbuildingAgent(MockAgent):
    """
    Worldbuilding Agent creates the rules and structure of the story world.
    
    Generates world rules, locations, and initial timeline.
    """
    
    def __init__(self):
        """Initialize the Worldbuilding Agent."""
        super().__init__(name="Worldbuilding Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute worldbuilding.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Create world rules
        world_rules = self._create_mock_world_rules()
        bible.world_rules = world_rules
        
        # Create key locations
        locations = self._create_mock_locations()
        for location in locations:
            bible.add_location(location)
            
        # Create initial timeline
        timeline_events = self._create_mock_timeline()
        for event in timeline_events:
            bible.add_timeline_event(event)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "world_rules": world_rules.to_dict(),
                "locations": len(locations),
                "timeline_events": len(timeline_events)
            },
            summary=f"Created world with {len(locations)} locations and {len(timeline_events)} timeline events"
        )
        
        self.log_action(f"Built world: {len(locations)} locations, {len(timeline_events)} timeline events")
        self.log_end(success=True)
        
        return {
            "success": True,
            "world_rules": world_rules.to_dict(),
            "locations_count": len(locations),
            "timeline_events_count": len(timeline_events)
        }
        
    def _create_mock_world_rules(self) -> WorldRules:
        """Create mock world rules for MVP."""
        return WorldRules(
            magic_system="Elemental magic drawn from nature; requires training and innate ability",
            technology_level="Medieval with some magical enhancements",
            social_structure="Feudal kingdom with noble houses and a royal family",
            key_rules=[
                "Magic users are rare and often feared",
                "Ancient artifacts hold immense power",
                "The kingdom is protected by magical barriers",
                "Dark magic corrupts those who use it"
            ]
        )
        
    def _create_mock_locations(self) -> list:
        """Create mock locations for MVP."""
        return [
            Location(
                name="The Capital City",
                description="A bustling medieval city with towering spires and magical defenses",
                significance="Center of political power and home to the royal family"
            ),
            Location(
                name="The Ancient Forest",
                description="A mystical forest where magic is strongest and ancient creatures dwell",
                significance="Source of magical power and location of key discoveries"
            ),
            Location(
                name="The Dark Fortress",
                description="A foreboding castle in the northern mountains, shrouded in darkness",
                significance="Stronghold of the antagonist and final battle location"
            )
        ]
        
    def _create_mock_timeline(self) -> list:
        """Create mock timeline events for MVP."""
        return [
            TimelineEvent(
                timestamp="1000 years ago",
                event="The Great War between light and dark magic ended with the sealing of dark powers"
            ),
            TimelineEvent(
                timestamp="100 years ago",
                event="The current royal dynasty was established after defeating the last dark lord"
            ),
            TimelineEvent(
                timestamp="Present day",
                event="Strange disturbances suggest the ancient seals are weakening"
            )
        ]

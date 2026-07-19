"""Worldbuilding Agent - Creates world rules and settings."""

import asyncio
import json
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..models import WorldRules, Location, TimelineEvent
from ..utils.prompts import PromptTemplates


class WorldbuildingAgent(AIAgent):
    """
    Worldbuilding Agent creates the rules and structure of the story world.
    
    Uses AI to generate world rules, locations, and initial timeline.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Worldbuilding Agent."""
        super().__init__(
            name="Worldbuilding Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.8,  # Higher temperature for creativity
            default_max_tokens=2500
        )
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute worldbuilding.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Generate world with AI
        world_data = asyncio.run(self._generate_world(bible))
        
        # Update Story Bible
        bible.world_rules = world_data["world_rules"]
        for location in world_data["locations"]:
            bible.add_location(location)
        for event in world_data["timeline_events"]:
            bible.add_timeline_event(event)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "world_rules": world_data["world_rules"].to_dict(),
                "locations": len(world_data["locations"]),
                "timeline_events": len(world_data["timeline_events"])
            },
            summary=f"Created world with {len(world_data['locations'])} locations and {len(world_data['timeline_events'])} timeline events"
        )
        
        self.log_action(f"Built world: {len(world_data['locations'])} locations, {len(world_data['timeline_events'])} timeline events")
        self.log_end(success=True)
        
        return {
            "success": True,
            "world_rules": world_data["world_rules"].to_dict(),
            "locations_count": len(world_data["locations"]),
            "timeline_events_count": len(world_data["timeline_events"])
        }
    
    async def _generate_world(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Generate world using AI.
        
        Args:
            bible: Story Bible with concept information
            
        Returns:
            Dictionary with world_rules, locations, and timeline_events
        """
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.WORLDBUILDING,
            genre=bible.brief.genre,
            logline=bible.concept.logline,
            theme=bible.concept.theme,
            setting="Fantasy kingdom with magic"  # Could be extracted from premise
        )
        
        # Generate world with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.8,
            max_tokens=2500
        )
        
        # Parse AI response
        world_data = self._parse_world_response(response.content)
        
        return world_data
    
    def _parse_world_response(self, ai_response: str) -> Dict[str, Any]:
        """
        Parse AI response into world components.
        
        Args:
            ai_response: Raw AI response text
            
        Returns:
            Dictionary with world_rules, locations, and timeline_events
        """
        # Initialize result
        result = {
            "world_rules": None,
            "locations": [],
            "timeline_events": []
        }
        
        # Try to extract structured data
        lines = ai_response.strip().split('\n')
        
        # Extract sections
        magic_system = ""
        technology_level = ""
        social_structure = ""
        key_rules = []
        locations = []
        timeline = []
        
        current_section = None
        current_location = {}
        current_event = {}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Detect sections
            if 'magic' in line.lower() and ('system' in line.lower() or ':' in line):
                current_section = 'magic'
                if ':' in line:
                    magic_system = line.split(':', 1)[1].strip()
            elif 'technology' in line.lower() and ':' in line:
                current_section = 'technology'
                technology_level = line.split(':', 1)[1].strip()
            elif 'social' in line.lower() and ('structure' in line.lower() or 'government' in line.lower()):
                current_section = 'social'
                if ':' in line:
                    social_structure = line.split(':', 1)[1].strip()
            elif 'rules' in line.lower() or 'laws' in line.lower():
                current_section = 'rules'
            elif 'location' in line.lower() or 'place' in line.lower():
                current_section = 'locations'
                if current_location and 'name' in current_location:
                    locations.append(current_location)
                current_location = {}
            elif 'history' in line.lower() or 'timeline' in line.lower():
                current_section = 'timeline'
            elif current_section == 'magic' and not magic_system:
                magic_system = line
            elif current_section == 'technology' and not technology_level:
                technology_level = line
            elif current_section == 'social' and not social_structure:
                social_structure = line
            elif current_section == 'rules' and line.startswith(('-', '•', '*')):
                key_rules.append(line.lstrip('-•* '))
            elif current_section == 'locations':
                if 'name' in line.lower() and ':' in line:
                    if current_location and 'name' in current_location:
                        locations.append(current_location)
                    current_location = {'name': line.split(':', 1)[1].strip()}
                elif 'description' in line.lower() and ':' in line:
                    current_location['description'] = line.split(':', 1)[1].strip()
                elif 'significance' in line.lower() and ':' in line:
                    current_location['significance'] = line.split(':', 1)[1].strip()
            elif current_section == 'timeline':
                if line.startswith(('-', '•', '*')) or 'ago' in line.lower() or 'year' in line.lower():
                    # Parse timeline event
                    event_text = line.lstrip('-•* ')
                    if ':' in event_text:
                        timestamp, event = event_text.split(':', 1)
                        timeline.append({'timestamp': timestamp.strip(), 'event': event.strip()})
                    else:
                        timeline.append({'timestamp': 'Unknown', 'event': event_text})
        
        # Add last location if exists
        if current_location and 'name' in current_location:
            locations.append(current_location)
        
        # Create WorldRules
        result["world_rules"] = WorldRules(
            magic_system=magic_system or "Magic system to be defined",
            technology_level=technology_level or "Technology level to be defined",
            social_structure=social_structure or "Social structure to be defined",
            key_rules=key_rules if key_rules else ["World rules to be defined"]
        )
        
        # Create Locations
        for loc_data in locations:
            if 'name' in loc_data:
                result["locations"].append(Location(
                    name=loc_data.get('name', 'Unnamed Location'),
                    description=loc_data.get('description', 'Description to be added'),
                    significance=loc_data.get('significance', 'Significance to be determined')
                ))
        
        # Create Timeline Events
        for event_data in timeline:
            result["timeline_events"].append(TimelineEvent(
                timestamp=event_data.get('timestamp', 'Unknown'),
                event=event_data.get('event', 'Event to be defined')
            ))
        
        # Ensure minimum data
        if not result["locations"]:
            result["locations"] = self._create_default_locations()
        if not result["timeline_events"]:
            result["timeline_events"] = self._create_default_timeline()
        
        return result
    
    def _create_default_locations(self) -> List[Location]:
        """Create default locations as fallback."""
        return [
            Location(
                name="The Capital",
                description="Main city and center of power",
                significance="Political and cultural center"
            ),
            Location(
                name="The Wilderness",
                description="Untamed lands beyond civilization",
                significance="Source of mystery and danger"
            )
        ]
    
    def _create_default_timeline(self) -> List[TimelineEvent]:
        """Create default timeline as fallback."""
        return [
            TimelineEvent(
                timestamp="Ancient times",
                event="The world was shaped by powerful forces"
            ),
            TimelineEvent(
                timestamp="Present day",
                event="The story begins"
            )
        ]
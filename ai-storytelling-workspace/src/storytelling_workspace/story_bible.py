"""Story Bible - Central state management for the storytelling workspace."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .models import (
    Character, Location, TimelineEvent, PlotThread, Chapter,
    AgentDelta, BookBrief, Concept, WorldRules
)


class StoryBible:
    """
    Central repository of story information.
    
    Maintains consistency across all agents by providing a single source of truth
    for characters, world rules, timeline, plot threads, and manuscript content.
    """
    
    def __init__(self, project_name: str = "Untitled"):
        """Initialize a new Story Bible."""
        self.project_name = project_name
        self.version = 0
        self.created_at = datetime.now().isoformat()
        self.last_updated = self.created_at
        
        # Core sections
        self.brief = BookBrief()
        self.concept = Concept()
        self.world_rules = WorldRules()
        self.characters: Dict[str, Character] = {}
        self.locations: Dict[str, Location] = {}
        self.timeline: List[TimelineEvent] = []
        self.plot_threads: Dict[str, PlotThread] = {}
        self.chapters: Dict[int, Chapter] = {}
        
        # Metadata and tracking
        self.terminology: Dict[str, str] = {}  # Special terms and their definitions
        self.style_guide: Dict[str, str] = {}  # Style preferences
        self.deltas: List[AgentDelta] = []  # History of agent changes
        self.metadata: Dict[str, Any] = {}  # Additional metadata
        
    def add_character(self, character: Character) -> None:
        """Add or update a character."""
        self.characters[character.name] = character
        self._bump_version()
        
    def add_location(self, location: Location) -> None:
        """Add or update a location."""
        self.locations[location.name] = location
        self._bump_version()
        
    def add_timeline_event(self, event: TimelineEvent) -> None:
        """Add an event to the timeline."""
        self.timeline.append(event)
        self._bump_version()
        
    def add_plot_thread(self, thread: PlotThread) -> None:
        """Add or update a plot thread."""
        self.plot_threads[thread.name] = thread
        self._bump_version()
        
    def add_chapter(self, chapter: Chapter) -> None:
        """Add or update a chapter."""
        self.chapters[chapter.number] = chapter
        self._bump_version()
        
    def record_delta(self, agent_name: str, changes: Dict[str, Any], summary: str) -> None:
        """Record changes made by an agent."""
        delta = AgentDelta(
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            changes=changes,
            summary=summary
        )
        self.deltas.append(delta)
        self._bump_version()
        
    def get_character(self, name: str) -> Optional[Character]:
        """Get a character by name."""
        return self.characters.get(name)
        
    def get_chapter(self, number: int) -> Optional[Chapter]:
        """Get a chapter by number."""
        return self.chapters.get(number)
        
    def get_chapters_in_order(self) -> List[Chapter]:
        """Get all chapters sorted by number."""
        return [self.chapters[num] for num in sorted(self.chapters.keys())]
        
    def _bump_version(self) -> None:
        """Increment version and update timestamp."""
        self.version += 1
        self.last_updated = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert Story Bible to dictionary for JSON serialization."""
        return {
            "project_name": self.project_name,
            "version": self.version,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "brief": self.brief.to_dict(),
            "concept": self.concept.to_dict(),
            "world_rules": self.world_rules.to_dict(),
            "characters": {name: char.to_dict() for name, char in self.characters.items()},
            "locations": {name: loc.to_dict() for name, loc in self.locations.items()},
            "timeline": [event.to_dict() for event in self.timeline],
            "plot_threads": {name: thread.to_dict() for name, thread in self.plot_threads.items()},
            "chapters": {num: chapter.to_dict() for num, chapter in self.chapters.items()},
            "terminology": self.terminology,
            "style_guide": self.style_guide,
            "deltas": [delta.to_dict() for delta in self.deltas],
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryBible':
        """Create Story Bible from dictionary."""
        bible = cls(project_name=data.get("project_name", "Untitled"))
        bible.version = data.get("version", 0)
        bible.created_at = data.get("created_at", datetime.now().isoformat())
        bible.last_updated = data.get("last_updated", datetime.now().isoformat())
        
        # Restore brief
        if "brief" in data:
            bible.brief = BookBrief(**data["brief"])
            
        # Restore concept
        if "concept" in data:
            bible.concept = Concept(**data["concept"])
            
        # Restore world rules
        if "world_rules" in data:
            bible.world_rules = WorldRules(**data["world_rules"])
            
        # Restore characters
        if "characters" in data:
            bible.characters = {
                name: Character(**char_data)
                for name, char_data in data["characters"].items()
            }
            
        # Restore locations
        if "locations" in data:
            bible.locations = {
                name: Location(**loc_data)
                for name, loc_data in data["locations"].items()
            }
            
        # Restore timeline
        if "timeline" in data:
            bible.timeline = [TimelineEvent(**event) for event in data["timeline"]]
            
        # Restore plot threads
        if "plot_threads" in data:
            bible.plot_threads = {
                name: PlotThread(**thread_data)
                for name, thread_data in data["plot_threads"].items()
            }
            
        # Restore chapters
        if "chapters" in data:
            bible.chapters = {
                int(num): Chapter(**chapter_data)
                for num, chapter_data in data["chapters"].items()
            }
            
        # Restore metadata
        bible.terminology = data.get("terminology", {})
        bible.style_guide = data.get("style_guide", {})
        bible.metadata = data.get("metadata", {})
        
        # Restore deltas
        if "deltas" in data:
            bible.deltas = [AgentDelta(**delta) for delta in data["deltas"]]
            
        return bible
        
    def save(self, filepath: Path) -> None:
        """Save Story Bible to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
    @classmethod
    def load(cls, filepath: Path) -> 'StoryBible':
        """Load Story Bible from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
        
    def get_summary(self) -> str:
        """Get a human-readable summary of the Story Bible state."""
        lines = [
            f"Story Bible: {self.project_name}",
            f"Version: {self.version}",
            f"Last Updated: {self.last_updated}",
            "",
            f"Characters: {len(self.characters)}",
            f"Locations: {len(self.locations)}",
            f"Timeline Events: {len(self.timeline)}",
            f"Plot Threads: {len(self.plot_threads)}",
            f"Chapters: {len(self.chapters)}",
            f"Agent Updates: {len(self.deltas)}",
        ]
        return "\n".join(lines)

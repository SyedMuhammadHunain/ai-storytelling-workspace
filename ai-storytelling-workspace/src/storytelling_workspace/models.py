"""Data models for Story Bible components."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Character:
    """
    Character profile in the story.
    
    Represents a character with their role, goals, flaws, and development arc.
    Used by Character Agent to create character profiles and by other agents
    to maintain character consistency throughout the story.
    """
    name: str  # Character's full name
    role: str  # Character's role: "protagonist", "antagonist", or "supporting"
    goals: List[str] = field(default_factory=list)  # Character's motivations and objectives
    flaws: List[str] = field(default_factory=list)  # Character weaknesses and vulnerabilities
    arc: str = ""  # Character's development arc throughout the story
    voice_signature: str = ""  # Distinctive speech patterns and vocabulary
    physical_description: str = ""  # Appearance and physical characteristics
    backstory: str = ""  # Character's history and background
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class Location:
    """
    Location or setting in the story world.
    
    Represents a place where story events occur. Used by Worldbuilding Agent
    to establish the story's physical environment and by other agents to
    maintain setting consistency.
    """
    name: str  # Location name (e.g., "The Crystal Tower", "Darkwood Forest")
    description: str  # Physical description and atmosphere
    significance: str = ""  # Role in the story and thematic importance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class TimelineEvent:
    """
    Event in the story timeline.
    
    Represents a significant event in the story's chronology. Used by
    Worldbuilding Agent to establish backstory and by Continuity Agent
    to check for timeline consistency.
    """
    timestamp: str  # When the event occurs (e.g., "Year 1205", "Three days before")
    event: str  # Description of what happens
    chapter: Optional[int] = None  # Chapter number where event occurs (if applicable)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class PlotThread:
    """
    A plot thread or subplot.
    
    Represents a narrative thread that spans multiple chapters. Used by
    Plot Architect to structure the story and by Continuity Agent to
    ensure plot threads are properly resolved.
    """
    name: str  # Thread name (e.g., "The Quest for the Artifact")
    description: str  # What this thread is about
    status: str = "active"  # Current status: "active", "resolved", or "abandoned"
    chapters: List[int] = field(default_factory=list)  # Chapters where this thread appears
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class Chapter:
    """
    Chapter outline and content.
    
    Represents a single chapter with its structure and text. Created by
    Plot Architect (outline) and filled by Chapter Drafting Agent (content).
    Updated by editing agents during revision phases.
    """
    number: int  # Chapter number (1-based)
    title: str  # Chapter title
    pov: str  # Point of view character for this chapter
    goal: str  # What the protagonist wants to achieve in this chapter
    conflict: str  # Main obstacle or challenge in this chapter
    word_count_target: int  # Target word count for this chapter
    content: str = ""  # Actual chapter text (empty until drafted)
    status: str = "planned"  # Status: "planned", "drafted", "edited", or "final"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class AgentDelta:
    """
    Record of changes made by an agent.
    
    Tracks what each agent modified in the Story Bible, providing a complete
    audit trail of how the story evolved. Used for debugging, rollback, and
    understanding the creative process.
    """
    agent_name: str  # Name of the agent that made the changes
    timestamp: str  # ISO 8601 timestamp when changes were made
    changes: Dict[str, Any]  # Dictionary describing what changed
    summary: str  # Human-readable summary of the changes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class BookBrief:
    """
    Initial book parameters from intake.
    
    Captures the author's vision and requirements for the book. Created by
    Intake Agent and used by all subsequent agents to guide their work.
    """
    genre: str = ""  # Book genre (e.g., "Fantasy", "Science Fiction", "Mystery")
    premise: str = ""  # One-sentence story premise
    target_length: int = 0  # Target word count for the complete manuscript
    tone: str = ""  # Overall tone (e.g., "dark", "humorous", "epic")
    audience: str = ""  # Target audience (e.g., "Young Adult", "Adult")
    pov: str = ""  # Narrative perspective: "first person", "third person limited", etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class Concept:
    """
    Expanded concept from brief.
    
    Develops the initial premise into a fuller concept with theme and conflict.
    Created by Concept Agent and used to guide worldbuilding and character
    development.
    """
    logline: str = ""  # One-sentence story summary (elevator pitch)
    premise: str = ""  # Expanded premise with more detail
    central_conflict: str = ""  # Main conflict driving the story
    theme: str = ""  # Central theme or message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class WorldRules:
    """
    Rules and constraints of the story world.
    
    Defines how the story world works, including magic systems, technology,
    and social structures. Created by Worldbuilding Agent and used by all
    agents to maintain world consistency.
    """
    magic_system: str = ""  # How magic works (if applicable)
    technology_level: str = ""  # Level of technological development
    social_structure: str = ""  # How society is organized
    key_rules: List[str] = field(default_factory=list)  # Important world rules and constraints
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
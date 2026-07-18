"""Data models for Story Bible components."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Character:
    """Character profile in the story."""
    name: str
    role: str  # protagonist, antagonist, supporting
    goals: List[str] = field(default_factory=list)
    flaws: List[str] = field(default_factory=list)
    arc: str = ""
    voice_signature: str = ""
    physical_description: str = ""
    backstory: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Location:
    """Location or setting in the story world."""
    name: str
    description: str
    significance: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TimelineEvent:
    """Event in the story timeline."""
    timestamp: str
    event: str
    chapter: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PlotThread:
    """A plot thread or subplot."""
    name: str
    description: str
    status: str = "active"  # active, resolved, abandoned
    chapters: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Chapter:
    """Chapter outline and content."""
    number: int
    title: str
    pov: str
    goal: str
    conflict: str
    word_count_target: int
    content: str = ""
    status: str = "planned"  # planned, drafted, edited, final
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AgentDelta:
    """Record of changes made by an agent."""
    agent_name: str
    timestamp: str
    changes: Dict[str, Any]
    summary: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class BookBrief:
    """Initial book parameters from intake."""
    genre: str = ""
    premise: str = ""
    target_length: int = 0  # word count
    tone: str = ""
    audience: str = ""
    pov: str = ""  # first person, third person, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Concept:
    """Expanded concept from brief."""
    logline: str = ""
    premise: str = ""
    central_conflict: str = ""
    theme: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class WorldRules:
    """Rules and constraints of the story world."""
    magic_system: str = ""
    technology_level: str = ""
    social_structure: str = ""
    key_rules: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

"""Pydantic schemas for Story Bible management."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Response schemas
class StoryBibleResponse(BaseModel):
    """Schema for Story Bible response."""
    
    id: UUID = Field(..., description="Story Bible UUID")
    project_id: UUID = Field(..., description="Project UUID")
    version: int = Field(..., ge=1, description="Story Bible version")
    brief: Optional[dict[str, Any]] = Field(None, description="Book brief")
    concept: Optional[dict[str, Any]] = Field(None, description="Concept and premise")
    world_rules: Optional[dict[str, Any]] = Field(None, description="World building rules")
    characters: Optional[dict[str, Any]] = Field(None, description="Character information")
    locations: Optional[dict[str, Any]] = Field(None, description="Location details")
    timeline: Optional[list[dict[str, Any]]] = Field(None, description="Story timeline")
    plot_threads: Optional[dict[str, Any]] = Field(None, description="Plot threads and arcs")
    terminology: Optional[dict[str, Any]] = Field(None, description="Terminology and lore")
    style_guide: Optional[dict[str, Any]] = Field(None, description="Writing style guide")
    metadata: Optional[dict[str, Any]] = Field(None, validation_alias="story_metadata", description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "version": 2,
                "brief": {
                    "genre": "Fantasy",
                    "premise": "A young mage discovers forbidden magic",
                    "target_audience": "Young Adult"
                },
                "concept": {
                    "logline": "When a forbidden spell awakens...",
                    "theme": "Power and responsibility"
                },
                "world_rules": {
                    "magic_system": "Elemental-based with strict rules",
                    "technology_level": "Medieval with magical enhancements"
                },
                "characters": {
                    "protagonist": {
                        "name": "Aria",
                        "age": 17,
                        "traits": ["curious", "impulsive", "brave"]
                    }
                },
                "locations": {
                    "academy": {
                        "name": "Silverwind Academy",
                        "description": "Ancient school of magic"
                    }
                },
                "timeline": {
                    "story_duration": "6 months",
                    "key_events": []
                },
                "plot_threads": {
                    "main": "Discovery of forbidden magic",
                    "subplots": ["Romance", "Betrayal"]
                },
                "terminology": {
                    "magic_terms": ["Weaving", "Channeling"]
                },
                "style_guide": {
                    "pov": "Third person limited",
                    "tense": "Past tense",
                    "tone": "Adventurous with dark undertones"
                },
                "metadata": {
                    "last_modified_by": "plot_architect",
                    "change_count": 15
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }
    }


class CharacterResponse(BaseModel):
    """Schema for individual character from Story Bible."""
    
    name: str = Field(..., description="Character name")
    role: str = Field(..., description="Character role (protagonist, antagonist, etc.)")
    age: Optional[int] = Field(None, ge=0, le=200, description="Character age")
    traits: list[str] = Field(default_factory=list, description="Character traits")
    arc: str = Field(..., description="Character arc description")
    voice_signature: str = Field(..., description="Character's unique voice/speech pattern")
    appearance: Optional[str] = Field(None, description="Physical appearance")
    backstory: Optional[str] = Field(None, description="Character backstory")
    goals: Optional[str] = Field(None, description="Character goals")
    flaws: Optional[str] = Field(None, description="Character flaws")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Aria Stormwind",
                "role": "protagonist",
                "age": 17,
                "traits": ["curious", "impulsive", "brave", "loyal"],
                "arc": "From naive student to responsible leader",
                "voice_signature": "Direct, uses modern slang, asks lots of questions",
                "appearance": "Tall with silver hair and violet eyes",
                "backstory": "Orphaned at age 5, raised by the Academy",
                "goals": "Master forbidden magic to save her mentor",
                "flaws": "Impulsive, struggles with authority"
            }
        }
    }


class LocationResponse(BaseModel):
    """Schema for individual location from Story Bible."""
    
    name: str = Field(..., description="Location name")
    type: str = Field(..., description="Location type (city, building, etc.)")
    description: str = Field(..., description="Location description")
    significance: Optional[str] = Field(None, description="Story significance")
    atmosphere: Optional[str] = Field(None, description="Atmosphere/mood")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Silverwind Academy",
                "type": "school",
                "description": "Ancient magical academy built into a mountain",
                "significance": "Where protagonist learns forbidden magic",
                "atmosphere": "Mysterious, ancient, filled with secrets"
            }
        }
    }


class PlotThreadResponse(BaseModel):
    """Schema for plot thread from Story Bible."""
    
    name: str = Field(..., description="Plot thread name")
    type: str = Field(..., description="Thread type (main, subplot)")
    description: str = Field(..., description="Thread description")
    status: str = Field(..., description="Thread status (active, resolved, abandoned)")
    chapters: list[int] = Field(default_factory=list, description="Chapters where thread appears")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Forbidden Magic Discovery",
                "type": "main",
                "description": "Aria discovers and learns to control forbidden magic",
                "status": "active",
                "chapters": [1, 3, 5, 8, 12, 15, 20, 25]
            }
        }
    }


class StoryBibleVersionListResponse(BaseModel):
    """Schema for list of Story Bible versions."""
    
    versions: list[dict[str, Any]] = Field(
        ...,
        description="List of Story Bible versions"
    )
    current_version: int = Field(..., ge=1, description="Current version number")
    total_versions: int = Field(..., ge=1, description="Total number of versions")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "versions": [
                    {
                        "version": 1,
                        "created_at": "2024-01-01T00:00:00Z",
                        "changes": "Initial version"
                    },
                    {
                        "version": 2,
                        "created_at": "2024-01-01T12:00:00Z",
                        "changes": "Added subplot threads"
                    }
                ],
                "current_version": 2,
                "total_versions": 2
            }
        }
    }

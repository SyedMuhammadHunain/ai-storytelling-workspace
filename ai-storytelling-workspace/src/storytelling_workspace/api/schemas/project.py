"""Pydantic schemas for project management."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Request schemas
class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Project name"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Project description"
    )
    genre: Optional[str] = Field(
        None,
        max_length=100,
        description="Book genre (e.g., Fantasy, Sci-Fi, Romance)"
    )
    target_length: int = Field(
        80000,
        ge=10000,
        le=200000,
        description="Target word count for the novel"
    )
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate name is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def description_strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace from description."""
        if v:
            return v.strip()
        return v


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Project name"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Project description"
    )
    genre: Optional[str] = Field(
        None,
        max_length=100,
        description="Book genre"
    )
    target_length: Optional[int] = Field(
        None,
        ge=10000,
        le=200000,
        description="Target word count"
    )
    status: Optional[Literal[
        'draft',
        'in_progress',
        'paused',
        'completed',
        'archived'
    ]] = Field(
        None,
        description="Project status"
    )
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate name is not empty or whitespace only."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Name cannot be empty or whitespace only')
            return v.strip()
        return v


# Response schemas
class ProjectResponse(BaseModel):
    """Schema for project response."""
    
    id: UUID = Field(..., description="Project UUID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    genre: Optional[str] = Field(None, description="Book genre")
    target_length: int = Field(..., description="Target word count")
    status: str = Field(..., description="Project status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "The Dragon's Quest",
                "description": "An epic fantasy adventure",
                "genre": "Fantasy",
                "target_length": 80000,
                "status": "in_progress",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    }


class ProjectListResponse(BaseModel):
    """Schema for paginated list of projects."""
    
    projects: list[ProjectResponse] = Field(
        ...,
        description="List of projects"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of projects"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number"
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "projects": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "The Dragon's Quest",
                        "description": "An epic fantasy adventure",
                        "genre": "Fantasy",
                        "target_length": 80000,
                        "status": "in_progress",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 20
            }
        }
    }


class ProjectStatsResponse(BaseModel):
    """Schema for project statistics."""
    
    project_id: UUID = Field(..., description="Project UUID")
    status: str = Field(..., description="Project status")
    word_count: int = Field(0, ge=0, description="Current word count")
    chapter_count: int = Field(0, ge=0, description="Number of chapters")
    image_count: int = Field(0, ge=0, description="Number of images")
    checkpoint_count: int = Field(0, ge=0, description="Number of checkpoints")
    bible_version: int = Field(0, ge=0, description="Story Bible version")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "in_progress",
                "word_count": 45000,
                "chapter_count": 15,
                "image_count": 8,
                "checkpoint_count": 3,
                "bible_version": 2
            }
        }
    }

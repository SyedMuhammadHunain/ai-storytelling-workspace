"""Pydantic schemas for image management."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Response schemas
class ImageResponse(BaseModel):
    """Schema for image metadata response."""
    
    id: UUID = Field(..., description="Image UUID")
    project_id: UUID = Field(..., description="Project UUID")
    story_bible_id: UUID = Field(..., description="Story Bible UUID")
    image_type: Literal[
        'cover_art',
        'character_portrait',
        'scene_illustration'
    ] = Field(..., description="Type of image")
    file_path: str = Field(..., description="File path relative to storage root")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    prompt: str = Field(..., description="Generation prompt used")
    model: str = Field(..., description="AI model used for generation")
    provider: str = Field(..., description="AI provider (pixtral, dall-e-3)")
    width: int = Field(..., ge=1, description="Image width in pixels")
    height: int = Field(..., ge=1, description="Image height in pixels")
    format: str = Field(..., description="Image format (png, jpg, webp)")
    character_name: Optional[str] = Field(
        None,
        description="Character name (for portraits)"
    )
    chapter_number: Optional[int] = Field(
        None,
        ge=1,
        description="Chapter number (for scene illustrations)"
    )
    generation_cost: float = Field(
        ...,
        ge=0.0,
        description="Generation cost in USD"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "story_bible_id": "123e4567-e89b-12d3-a456-426614174002",
                "image_type": "cover_art",
                "file_path": "images/project_123/cover_art.png",
                "file_size": 2048576,
                "prompt": "Epic fantasy book cover featuring a young mage with silver hair...",
                "model": "pixtral-large-latest",
                "provider": "pixtral",
                "width": 1024,
                "height": 1024,
                "format": "png",
                "character_name": None,
                "chapter_number": None,
                "generation_cost": 0.04,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    }


class ImageListResponse(BaseModel):
    """Schema for list of images."""
    
    images: list[ImageResponse] = Field(..., description="List of images")
    total: int = Field(..., ge=0, description="Total number of images")
    by_type: dict[str, int] = Field(
        default_factory=dict,
        description="Count of images by type"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "images": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "project_id": "123e4567-e89b-12d3-a456-426614174001",
                        "story_bible_id": "123e4567-e89b-12d3-a456-426614174002",
                        "image_type": "cover_art",
                        "file_path": "images/project_123/cover_art.png",
                        "file_size": 2048576,
                        "prompt": "Epic fantasy book cover...",
                        "model": "pixtral-large-latest",
                        "provider": "pixtral",
                        "width": 1024,
                        "height": 1024,
                        "format": "png",
                        "character_name": None,
                        "chapter_number": None,
                        "generation_cost": 0.04,
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 8,
                "by_type": {
                    "cover_art": 1,
                    "character_portrait": 4,
                    "scene_illustration": 3
                }
            }
        }
    }


class ImageGenerationRequest(BaseModel):
    """Schema for requesting image generation."""
    
    image_type: Literal[
        'cover_art',
        'character_portrait',
        'scene_illustration'
    ] = Field(..., description="Type of image to generate")
    prompt: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Generation prompt"
    )
    character_name: Optional[str] = Field(
        None,
        description="Character name (required for portraits)"
    )
    chapter_number: Optional[int] = Field(
        None,
        ge=1,
        description="Chapter number (required for scene illustrations)"
    )
    style_override: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional style override"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "image_type": "character_portrait",
                "prompt": "Portrait of Aria Stormwind, 17-year-old mage with silver hair and violet eyes...",
                "character_name": "Aria Stormwind",
                "chapter_number": None,
                "style_override": None
            }
        }
    }


class ImageGenerationResponse(BaseModel):
    """Schema for image generation response."""
    
    image_id: UUID = Field(..., description="Generated image UUID")
    status: Literal['queued', 'generating', 'completed', 'failed'] = Field(
        ...,
        description="Generation status"
    )
    message: str = Field(..., description="Status message")
    estimated_time_seconds: Optional[int] = Field(
        None,
        ge=0,
        description="Estimated generation time in seconds"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "image_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "queued",
                "message": "Image generation queued",
                "estimated_time_seconds": 30
            }
        }
    }


class ImageDownloadResponse(BaseModel):
    """Schema for image download information."""
    
    image_id: UUID = Field(..., description="Image UUID")
    download_url: str = Field(..., description="Temporary download URL")
    expires_at: datetime = Field(..., description="URL expiration time")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    format: str = Field(..., description="Image format")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "image_id": "123e4567-e89b-12d3-a456-426614174000",
                "download_url": "/api/images/123e4567-e89b-12d3-a456-426614174000/download",
                "expires_at": "2024-01-01T01:00:00Z",
                "file_size": 2048576,
                "format": "png"
            }
        }
    }

"""
Unit tests for Image model.
"""

import pytest
from decimal import Decimal

from storytelling_workspace.db.models import Image, ImageType


def test_image_creation():
    """Test creating an Image instance."""
    image = Image(
        project_id="test-project-id",
        story_bible_id="test-bible-id",
        image_type=ImageType.COVER_ART.value,
        file_path="/storage/images/cover.png",
        file_size=1024000,
        prompt="A fantasy book cover",
        model="pixtral-large-latest",
        provider="mistral",
        width=1024,
        height=1024,
        format="png",
        generation_cost=Decimal("0.0400"),
    )
    
    assert image.project_id == "test-project-id"
    assert image.story_bible_id == "test-bible-id"
    assert image.image_type == ImageType.COVER_ART.value
    assert image.file_path == "/storage/images/cover.png"
    assert image.file_size == 1024000
    assert image.width == 1024
    assert image.height == 1024


def test_image_type_properties():
    """Test image type properties."""
    cover = Image(
        project_id="test-id",
        story_bible_id="test-id",
        image_type=ImageType.COVER_ART.value,
        file_path="/test.png",
        file_size=1000,
        prompt="test",
        model="test",
        provider="test",
        width=100,
        height=100,
        format="png",
    )
    
    assert cover.is_cover_art
    assert not cover.is_character_portrait
    assert not cover.is_scene_illustration
    
    portrait = Image(
        project_id="test-id",
        story_bible_id="test-id",
        image_type=ImageType.CHARACTER_PORTRAIT.value,
        file_path="/test.png",
        file_size=1000,
        prompt="test",
        model="test",
        provider="test",
        width=100,
        height=100,
        format="png",
        character_name="John",
    )
    
    assert portrait.is_character_portrait
    assert portrait.character_name == "John"


def test_image_dimensions():
    """Test dimensions property."""
    image = Image(
        project_id="test-id",
        story_bible_id="test-id",
        image_type=ImageType.SCENE_ILLUSTRATION.value,
        file_path="/test.png",
        file_size=1000,
        prompt="test",
        model="test",
        provider="test",
        width=1920,
        height=1080,
        format="png",
    )
    
    assert image.dimensions == (1920, 1080)


def test_image_size_mb():
    """Test size_mb property."""
    image = Image(
        project_id="test-id",
        story_bible_id="test-id",
        image_type=ImageType.COVER_ART.value,
        file_path="/test.png",
        file_size=2097152,  # 2 MB
        prompt="test",
        model="test",
        provider="test",
        width=100,
        height=100,
        format="png",
    )
    
    assert image.size_mb == 2.0


def test_image_repr():
    """Test string representation."""
    image = Image(
        project_id="test-id",
        story_bible_id="test-id",
        image_type=ImageType.COVER_ART.value,
        file_path="/storage/cover.png",
        file_size=1000,
        prompt="test",
        model="test",
        provider="test",
        width=100,
        height=100,
        format="png",
    )
    
    repr_str = repr(image)
    
    assert "Image" in repr_str
    assert "cover_art" in repr_str
    assert "/storage/cover.png" in repr_str

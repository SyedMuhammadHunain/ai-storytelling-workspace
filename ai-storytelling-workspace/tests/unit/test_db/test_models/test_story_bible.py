"""
Unit tests for StoryBible model.
"""

import pytest

from storytelling_workspace.db.models import StoryBible


def test_story_bible_creation():
    """Test creating a StoryBible instance."""
    story_bible = StoryBible(
        project_id="test-project-id",
        version=1,
        brief={"title": "Test Novel", "premise": "A test premise"},
        concept={"themes": ["adventure", "mystery"]},
    )
    
    assert story_bible.project_id == "test-project-id"
    assert story_bible.version == 1
    assert story_bible.brief["title"] == "Test Novel"
    assert story_bible.concept["themes"] == ["adventure", "mystery"]


def test_story_bible_increment_version():
    """Test incrementing version number."""
    story_bible = StoryBible(project_id="test-id", version=1)
    
    assert story_bible.version == 1
    
    story_bible.increment_version()
    
    assert story_bible.version == 2


def test_story_bible_get_section():
    """Test getting a specific section."""
    story_bible = StoryBible(
        project_id="test-id",
        characters={"protagonist": {"name": "John"}},
        plot_threads={"main": "Main plot"},
    )
    
    characters = story_bible.get_section("characters")
    assert characters == {"protagonist": {"name": "John"}}
    
    plot = story_bible.get_section("plot_threads")
    assert plot == {"main": "Main plot"}
    
    missing = story_bible.get_section("nonexistent")
    assert missing is None


def test_story_bible_update_section():
    """Test updating a specific section."""
    story_bible = StoryBible(
        project_id="test-id",
        characters={"old": "data"},
    )
    
    new_data = {"protagonist": {"name": "Jane"}}
    story_bible.update_section("characters", new_data)
    
    assert story_bible.characters == new_data


def test_story_bible_repr():
    """Test string representation."""
    story_bible = StoryBible(project_id="test-id", version=3)
    repr_str = repr(story_bible)
    
    assert "StoryBible" in repr_str
    assert "test-id" in repr_str
    assert "version=3" in repr_str


def test_story_bible_all_sections():
    """Test all JSON sections can be set."""
    story_bible = StoryBible(
        project_id="test-id",
        brief={"test": "brief"},
        concept={"test": "concept"},
        world_rules={"test": "world"},
        characters={"test": "chars"},
        locations={"test": "locs"},
        timeline={"test": "time"},
        plot_threads={"test": "plot"},
        terminology={"test": "terms"},
        style_guide={"test": "style"},
        metadata={"test": "meta"},
    )
    
    assert story_bible.brief["test"] == "brief"
    assert story_bible.concept["test"] == "concept"
    assert story_bible.world_rules["test"] == "world"
    assert story_bible.characters["test"] == "chars"
    assert story_bible.locations["test"] == "locs"
    assert story_bible.timeline["test"] == "time"
    assert story_bible.plot_threads["test"] == "plot"
    assert story_bible.terminology["test"] == "terms"
    assert story_bible.style_guide["test"] == "style"
    assert story_bible.metadata["test"] == "meta"

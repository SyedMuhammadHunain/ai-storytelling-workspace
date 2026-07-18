"""Tests for Story Bible data structures and persistence."""

import pytest
import json
from pathlib import Path
from datetime import datetime

from storytelling_workspace.story_bible import StoryBible
from storytelling_workspace.models import (
    Character, Location, TimelineEvent, PlotThread, Chapter,
    BookBrief, Concept, WorldRules
)


def test_story_bible_initialization():
    """Test Story Bible can be initialized."""
    bible = StoryBible(project_name="Test Project")
    
    assert bible.project_name == "Test Project"
    assert bible.version == 0
    assert len(bible.characters) == 0
    assert len(bible.chapters) == 0


def test_add_character():
    """Test adding a character to Story Bible."""
    bible = StoryBible()
    
    character = Character(
        name="Alice",
        role="protagonist",
        goals=["Save the world"],
        flaws=["Too trusting"],
        arc="Hero's journey"
    )
    
    bible.add_character(character)
    
    assert len(bible.characters) == 1
    assert bible.get_character("Alice") == character
    assert bible.version == 1


def test_add_location():
    """Test adding a location to Story Bible."""
    bible = StoryBible()
    
    location = Location(
        name="Castle",
        description="Ancient fortress",
        significance="Final battle location"
    )
    
    bible.add_location(location)
    
    assert len(bible.locations) == 1
    assert "Castle" in bible.locations
    assert bible.version == 1


def test_add_chapter():
    """Test adding a chapter to Story Bible."""
    bible = StoryBible()
    
    chapter = Chapter(
        number=1,
        title="The Beginning",
        pov="Alice",
        goal="Introduce protagonist",
        conflict="Internal doubt",
        word_count_target=3000,
        content="Once upon a time..."
    )
    
    bible.add_chapter(chapter)
    
    assert len(bible.chapters) == 1
    assert bible.get_chapter(1) == chapter
    assert bible.version == 1


def test_get_chapters_in_order():
    """Test retrieving chapters in order."""
    bible = StoryBible()
    
    # Add chapters out of order
    bible.add_chapter(Chapter(number=3, title="Three", pov="Alice", goal="", conflict="", word_count_target=3000))
    bible.add_chapter(Chapter(number=1, title="One", pov="Alice", goal="", conflict="", word_count_target=3000))
    bible.add_chapter(Chapter(number=2, title="Two", pov="Bob", goal="", conflict="", word_count_target=3000))
    
    chapters = bible.get_chapters_in_order()
    
    assert len(chapters) == 3
    assert chapters[0].number == 1
    assert chapters[1].number == 2
    assert chapters[2].number == 3


def test_record_delta():
    """Test recording agent changes."""
    bible = StoryBible()
    
    bible.record_delta(
        agent_name="TestAgent",
        changes={"characters": ["Added Alice"]},
        summary="Added protagonist"
    )
    
    assert len(bible.deltas) == 1
    assert bible.deltas[0].agent_name == "TestAgent"
    assert bible.deltas[0].summary == "Added protagonist"
    assert bible.version == 1


def test_version_bumping():
    """Test that version increments with changes."""
    bible = StoryBible()
    initial_version = bible.version
    
    bible.add_character(Character(name="Alice", role="protagonist"))
    assert bible.version == initial_version + 1
    
    bible.add_location(Location(name="Castle", description="Old fortress"))
    assert bible.version == initial_version + 2
    
    bible.add_chapter(Chapter(number=1, title="Start", pov="Alice", goal="", conflict="", word_count_target=3000))
    assert bible.version == initial_version + 3


def test_to_dict():
    """Test converting Story Bible to dictionary."""
    bible = StoryBible(project_name="Test")
    bible.add_character(Character(name="Alice", role="protagonist"))
    
    data = bible.to_dict()
    
    assert isinstance(data, dict)
    assert data["project_name"] == "Test"
    assert "characters" in data
    assert "Alice" in data["characters"]
    assert data["version"] == 1


def test_from_dict():
    """Test creating Story Bible from dictionary."""
    original = StoryBible(project_name="Test")
    original.add_character(Character(name="Alice", role="protagonist"))
    original.add_chapter(Chapter(number=1, title="Start", pov="Alice", goal="", conflict="", word_count_target=3000))
    
    data = original.to_dict()
    restored = StoryBible.from_dict(data)
    
    assert restored.project_name == original.project_name
    assert restored.version == original.version
    assert len(restored.characters) == len(original.characters)
    assert len(restored.chapters) == len(original.chapters)
    assert restored.get_character("Alice").name == "Alice"


def test_save_and_load(tmp_path):
    """Test saving and loading Story Bible from file."""
    filepath = tmp_path / "story_bible.json"
    
    # Create and save
    original = StoryBible(project_name="Test Project")
    original.add_character(Character(name="Alice", role="protagonist"))
    original.add_location(Location(name="Castle", description="Old fortress"))
    original.save(filepath)
    
    # Load and verify
    loaded = StoryBible.load(filepath)
    
    assert loaded.project_name == original.project_name
    assert len(loaded.characters) == 1
    assert len(loaded.locations) == 1
    assert loaded.get_character("Alice").name == "Alice"


def test_get_summary():
    """Test getting a summary of Story Bible state."""
    bible = StoryBible(project_name="Test")
    bible.add_character(Character(name="Alice", role="protagonist"))
    bible.add_character(Character(name="Bob", role="antagonist"))
    bible.add_chapter(Chapter(number=1, title="Start", pov="Alice", goal="", conflict="", word_count_target=3000))
    
    summary = bible.get_summary()
    
    assert "Test" in summary
    assert "Characters: 2" in summary
    assert "Chapters: 1" in summary


def test_book_brief():
    """Test Book Brief data structure."""
    bible = StoryBible()
    bible.brief.genre = "Fantasy"
    bible.brief.premise = "A hero's journey"
    bible.brief.target_length = 80000
    
    data = bible.to_dict()
    
    assert data["brief"]["genre"] == "Fantasy"
    assert data["brief"]["target_length"] == 80000


def test_concept():
    """Test Concept data structure."""
    bible = StoryBible()
    bible.concept.logline = "A hero must save the world"
    bible.concept.theme = "Courage"
    
    data = bible.to_dict()
    
    assert data["concept"]["logline"] == "A hero must save the world"
    assert data["concept"]["theme"] == "Courage"


def test_world_rules():
    """Test World Rules data structure."""
    bible = StoryBible()
    bible.world_rules.magic_system = "Elemental magic"
    bible.world_rules.key_rules = ["Magic requires sacrifice", "No resurrection"]
    
    data = bible.to_dict()
    
    assert data["world_rules"]["magic_system"] == "Elemental magic"
    assert len(data["world_rules"]["key_rules"]) == 2

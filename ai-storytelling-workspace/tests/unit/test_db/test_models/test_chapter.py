"""
Unit tests for Chapter model.
"""

import pytest

from storytelling_workspace.db.models import Chapter, ChapterStatus


def test_chapter_creation():
    """Test creating a Chapter instance."""
    chapter = Chapter(
        story_bible_id="test-bible-id",
        chapter_number=1,
        title="Chapter One",
        content="This is the chapter content.",
        target_word_count=3000,
    )
    
    assert chapter.story_bible_id == "test-bible-id"
    assert chapter.chapter_number == 1
    assert chapter.title == "Chapter One"
    assert chapter.content == "This is the chapter content."
    assert chapter.target_word_count == 3000
    assert chapter.status == ChapterStatus.PLANNED


def test_chapter_update_word_count():
    """Test updating word count from content."""
    chapter = Chapter(
        story_bible_id="test-id",
        chapter_number=1,
        title="Test",
        content="This is a test chapter with words.",
    )
    
    chapter.update_word_count()
    
    assert chapter.word_count == 7


def test_chapter_update_word_count_empty():
    """Test updating word count with no content."""
    chapter = Chapter(
        story_bible_id="test-id",
        chapter_number=1,
        title="Test",
        content=None,
    )
    
    chapter.update_word_count()
    
    assert chapter.word_count == 0


def test_chapter_is_completed():
    """Test is_completed property."""
    chapter = Chapter(
        story_bible_id="test-id",
        chapter_number=1,
        title="Test",
        status=ChapterStatus.PLANNED,
    )
    
    assert not chapter.is_completed
    
    chapter.status = ChapterStatus.COMPLETED
    
    assert chapter.is_completed


def test_chapter_progress_percentage():
    """Test progress percentage calculation."""
    chapter = Chapter(
        story_bible_id="test-id",
        chapter_number=1,
        title="Test",
        word_count=1500,
        target_word_count=3000,
    )
    
    assert chapter.progress_percentage == 50.0
    
    chapter.word_count = 3000
    assert chapter.progress_percentage == 100.0
    
    chapter.word_count = 4000
    assert chapter.progress_percentage == 100.0  # Capped at 100


def test_chapter_repr():
    """Test string representation."""
    chapter = Chapter(
        story_bible_id="test-id",
        chapter_number=5,
        title="The Journey",
        status=ChapterStatus.IN_PROGRESS,
    )
    
    repr_str = repr(chapter)
    
    assert "Chapter" in repr_str
    assert "number=5" in repr_str
    assert "The Journey" in repr_str
    assert "in_progress" in repr_str

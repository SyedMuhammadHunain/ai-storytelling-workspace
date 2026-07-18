"""Tests for assembly phase agents."""

import pytest
import os
import tempfile
import shutil
from storytelling_workspace.agents.front_matter import FrontMatterAgent
from storytelling_workspace.agents.back_matter import BackMatterAgent
from storytelling_workspace.agents.compilation import CompilationAgent
from storytelling_workspace.agents.qa import QAAgent
from storytelling_workspace.agents.export import ExportAgent
from storytelling_workspace.agents.plot_architect import PlotArchitectAgent
from storytelling_workspace.agents.chapter_drafting import ChapterDraftingAgent
from storytelling_workspace.story_bible import StoryBible
from storytelling_workspace.models import BookBrief


# Front Matter Agent Tests

def test_front_matter_agent_initialization():
    """Test FrontMatterAgent can be initialized."""
    agent = FrontMatterAgent()
    assert agent.name == "Front Matter Agent"


def test_front_matter_agent_execute():
    """Test FrontMatterAgent executes and generates front matter."""
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="A hero's journey")
    
    agent = FrontMatterAgent()
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "front_matter" in result


def test_front_matter_agent_creates_sections():
    """Test FrontMatterAgent creates all required sections."""
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="A hero's journey")
    
    agent = FrontMatterAgent()
    agent.execute(bible)
    
    assert "front_matter" in bible.metadata
    front_matter = bible.metadata["front_matter"]
    assert "title_page" in front_matter
    assert "copyright" in front_matter
    assert "table_of_contents" in front_matter


def test_front_matter_agent_generates_toc():
    """Test FrontMatterAgent generates TOC from chapters."""
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="A hero's journey")
    
    # Add chapters
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    agent = FrontMatterAgent()
    agent.execute(bible)
    
    toc = bible.metadata["front_matter"]["table_of_contents"]
    assert "Chapter 1" in toc
    assert "Chapter 10" in toc


# Back Matter Agent Tests

def test_back_matter_agent_initialization():
    """Test BackMatterAgent can be initialized."""
    agent = BackMatterAgent()
    assert agent.name == "Back Matter Agent"


def test_back_matter_agent_execute():
    """Test BackMatterAgent executes and generates back matter."""
    bible = StoryBible(project_name="Test")
    
    agent = BackMatterAgent()
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "back_matter" in result


def test_back_matter_agent_creates_sections():
    """Test BackMatterAgent creates all required sections."""
    bible = StoryBible(project_name="Test")
    
    agent = BackMatterAgent()
    agent.execute(bible)
    
    assert "back_matter" in bible.metadata
    back_matter = bible.metadata["back_matter"]
    assert "acknowledgments" in back_matter
    assert "author_bio" in back_matter


# Compilation Agent Tests

def test_compilation_agent_initialization():
    """Test CompilationAgent can be initialized."""
    agent = CompilationAgent()
    assert agent.name == "Compilation Agent"


def test_compilation_agent_execute():
    """Test CompilationAgent executes and compiles manuscript."""
    bible = StoryBible(project_name="Test")
    
    # Add chapters
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    for i in range(1, 4):
        chapter_agent = ChapterDraftingAgent(chapter_number=i)
        chapter_agent.execute(bible)
    
    agent = CompilationAgent()
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "manuscript" in result
    assert result["word_count"] > 0


def test_compilation_agent_includes_front_matter():
    """Test CompilationAgent includes front matter in compilation."""
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="A hero's journey")
    
    # Add front matter
    front_agent = FrontMatterAgent()
    front_agent.execute(bible)
    
    # Add chapters
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    chapter_agent = ChapterDraftingAgent(chapter_number=1)
    chapter_agent.execute(bible)
    
    # Compile
    agent = CompilationAgent()
    result = agent.execute(bible)
    
    manuscript = result["manuscript"]
    assert "Copyright" in manuscript or "Table of Contents" in manuscript


def test_compilation_agent_includes_back_matter():
    """Test CompilationAgent includes back matter in compilation."""
    bible = StoryBible(project_name="Test")
    
    # Add back matter
    back_agent = BackMatterAgent()
    back_agent.execute(bible)
    
    # Add chapters
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    chapter_agent = ChapterDraftingAgent(chapter_number=1)
    chapter_agent.execute(bible)
    
    # Compile
    agent = CompilationAgent()
    result = agent.execute(bible)
    
    manuscript = result["manuscript"]
    assert "Acknowledgments" in manuscript or "About the Author" in manuscript


# QA Agent Tests

def test_qa_agent_initialization():
    """Test QAAgent can be initialized."""
    agent = QAAgent()
    assert agent.name == "QA Agent"


def test_qa_agent_execute():
    """Test QAAgent executes and validates manuscript."""
    bible = StoryBible(project_name="Test")
    
    agent = QAAgent()
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "issues" in result
    assert "report" in result


def test_qa_agent_detects_empty_chapters():
    """Test QAAgent detects chapters without content."""
    bible = StoryBible(project_name="Test")
    
    # Add outline but no content
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    agent = QAAgent()
    result = agent.execute(bible)
    
    # Should find issues for empty chapters
    assert result["issues"] is not None
    assert len(result["issues"]) > 0


def test_qa_agent_passes_complete_manuscript():
    """Test QAAgent passes complete manuscript."""
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="A hero's journey")
    
    # Add complete content
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    for i in range(1, 11):
        chapter_agent = ChapterDraftingAgent(chapter_number=i)
        chapter_agent.execute(bible)
    
    # Compile
    compilation_agent = CompilationAgent()
    compilation_agent.execute(bible)
    
    agent = QAAgent()
    result = agent.execute(bible)
    
    # Should have fewer issues with complete manuscript
    assert result["success"] is True


# Export Agent Tests

def test_export_agent_initialization():
    """Test ExportAgent can be initialized."""
    agent = ExportAgent()
    assert agent.name == "Export Agent"


def test_export_agent_execute():
    """Test ExportAgent executes and exports files."""
    bible = StoryBible(project_name="Test")
    
    # Add some content
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    chapter_agent = ChapterDraftingAgent(chapter_number=1)
    chapter_agent.execute(bible)
    
    # Create temp directory for export
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ExportAgent(output_dir=tmpdir)
        result = agent.execute(bible)
        
        assert result["success"] is True
        assert "manuscript_path" in result
        assert "story_bible_path" in result
        
        # Verify files exist
        assert os.path.exists(result["manuscript_path"])
        assert os.path.exists(result["story_bible_path"])


def test_export_agent_creates_output_directory():
    """Test ExportAgent creates output directory if it doesn't exist."""
    bible = StoryBible(project_name="Test")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = os.path.join(tmpdir, "new_output")
        agent = ExportAgent(output_dir=output_dir)
        agent.execute(bible)
        
        assert os.path.exists(output_dir)


def test_export_agent_exports_manuscript():
    """Test ExportAgent exports manuscript to text file."""
    bible = StoryBible(project_name="Test")
    
    # Add content
    plot_agent = PlotArchitectAgent()
    plot_agent.execute(bible)
    
    chapter_agent = ChapterDraftingAgent(chapter_number=1)
    chapter_agent.execute(bible)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ExportAgent(output_dir=tmpdir)
        result = agent.execute(bible)
        
        # Read manuscript file
        with open(result["manuscript_path"], "r") as f:
            content = f.read()
        
        assert len(content) > 0
        assert "Chapter 1" in content


def test_export_agent_exports_story_bible():
    """Test ExportAgent exports Story Bible to JSON."""
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="A hero's journey")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ExportAgent(output_dir=tmpdir)
        result = agent.execute(bible)
        
        # Load Story Bible from file
        loaded_bible = StoryBible.load(result["story_bible_path"])
        
        assert loaded_bible.project_name == "Test"
        assert loaded_bible.brief.genre == "Fantasy"


# Integration Tests

def test_all_assembly_agents_record_changes():
    """Test all assembly agents record changes to Story Bible."""
    bible = StoryBible(project_name="Test")
    bible.brief = BookBrief(genre="Fantasy", premise="A hero's journey")
    
    agents = [
        FrontMatterAgent(),
        BackMatterAgent(),
        CompilationAgent(),
        QAAgent()
    ]
    
    for agent in agents:
        agent.execute(bible)
    
    assert len(bible.deltas) == 4


def test_assembly_agents_increment_version():
    """Test assembly agents increment Story Bible version."""
    bible = StoryBible(project_name="Test")
    initial_version = bible.version
    
    agent = FrontMatterAgent()
    agent.execute(bible)
    
    assert bible.version > initial_version

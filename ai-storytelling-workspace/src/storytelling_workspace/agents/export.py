"""Export Agent - Outputs manuscript to files."""

import os
from pathlib import Path
from typing import Dict, Any

from .base import BaseAgent
from ..story_bible import StoryBible


class ExportAgent(BaseAgent):
    """
    Export Agent outputs manuscript and Story Bible to files.
    
    Creates output directory and exports to TXT and JSON formats.
    This is primarily a file I/O task, not requiring AI generation.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the Export Agent.
        
        Args:
            output_dir: Directory to export files to
        """
        super().__init__(name="Export Agent")
        self.output_dir = output_dir
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute export.
        
        Args:
            bible: Story Bible to export
            
        Returns:
            Execution results with file paths
        """
        self.log_start()
        
        # Create output directory
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export manuscript
        manuscript_path = self._export_manuscript(bible, output_path)
        
        # Export Story Bible
        story_bible_path = self._export_story_bible(bible, output_path)
        
        # Export individual chapters (optional)
        chapters_dir = self._export_chapters(bible, output_path)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "export": True,
                "manuscript_path": str(manuscript_path),
                "story_bible_path": str(story_bible_path),
                "chapters_dir": str(chapters_dir)
            },
            summary=f"Exported to {self.output_dir}/"
        )
        
        self.log_action(f"Exported manuscript to {manuscript_path}")
        self.log_action(f"Exported Story Bible to {story_bible_path}")
        self.log_action(f"Exported chapters to {chapters_dir}")
        self.log_end(success=True)
        
        return {
            "success": True,
            "manuscript_path": str(manuscript_path),
            "story_bible_path": str(story_bible_path),
            "chapters_dir": str(chapters_dir),
            "output_dir": self.output_dir
        }
    
    def _export_manuscript(self, bible: StoryBible, output_path: Path) -> Path:
        """
        Export manuscript to text file.
        
        Args:
            bible: Story Bible with manuscript
            output_path: Output directory path
            
        Returns:
            Path to exported manuscript
        """
        manuscript_path = output_path / "manuscript.txt"
        
        # Get compiled manuscript or compile on the fly
        if "manuscript_text" in bible.metadata:
            manuscript = bible.metadata["manuscript_text"]
        else:
            # Simple compilation if not already compiled
            manuscript = self._simple_compile(bible)
        
        manuscript_path.write_text(manuscript, encoding="utf-8")
        
        return manuscript_path
    
    def _export_story_bible(self, bible: StoryBible, output_path: Path) -> Path:
        """
        Export Story Bible to JSON file.
        
        Args:
            bible: Story Bible to export
            output_path: Output directory path
            
        Returns:
            Path to exported Story Bible
        """
        story_bible_path = output_path / "story_bible.json"
        bible.save(story_bible_path)
        return story_bible_path
    
    def _export_chapters(self, bible: StoryBible, output_path: Path) -> Path:
        """
        Export individual chapters to separate files.
        
        Args:
            bible: Story Bible with chapters
            output_path: Output directory path
            
        Returns:
            Path to chapters directory
        """
        chapters_dir = output_path / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        
        for chapter in sorted(bible.chapters, key=lambda c: c.number):
            if chapter.content:
                chapter_file = chapters_dir / f"chapter_{chapter.number:02d}_{chapter.title.replace(' ', '_')}.txt"
                chapter_file.write_text(chapter.content, encoding="utf-8")
        
        return chapters_dir
    
    def _simple_compile(self, bible: StoryBible) -> str:
        """
        Simple manuscript compilation if not already compiled.
        
        Args:
            bible: Story Bible with chapters
            
        Returns:
            Compiled manuscript text
        """
        parts = []
        
        # Add front matter if available
        if "front_matter" in bible.metadata:
            front = bible.metadata["front_matter"]
            for section in ["title_page", "copyright", "dedication", "table_of_contents"]:
                if section in front:
                    parts.append(front[section])
                    parts.append("\n\n" + "="*50 + "\n\n")
        
        # Add chapters
        for chapter in sorted(bible.chapters, key=lambda c: c.number):
            if chapter.content:
                parts.append(f"\n\n# Chapter {chapter.number}: {chapter.title}\n\n")
                parts.append(chapter.content)
                parts.append("\n\n" + "-"*50 + "\n\n")
        
        # Add back matter if available
        if "back_matter" in bible.metadata:
            back = bible.metadata["back_matter"]
            parts.append("\n\n" + "="*50 + "\n\n")
            for section in ["acknowledgments", "author_bio", "discussion_questions"]:
                if section in back:
                    parts.append(back[section])
                    parts.append("\n\n")
        
        return "".join(parts)
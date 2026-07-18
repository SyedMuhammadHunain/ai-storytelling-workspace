"""Export Agent - Outputs manuscript to files."""

import os
from pathlib import Path
from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible


class ExportAgent(MockAgent):
    """
    Export Agent outputs manuscript and Story Bible to files.
    
    Creates output directory and exports to TXT and JSON formats.
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
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Export manuscript
        manuscript_path = self._export_manuscript(bible)
        
        # Export Story Bible
        story_bible_path = self._export_story_bible(bible)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "export": True,
                "manuscript_path": manuscript_path,
                "story_bible_path": story_bible_path
            },
            summary=f"Exported to {self.output_dir}/"
        )
        
        self.log_action(f"Exported manuscript to {manuscript_path}")
        self.log_action(f"Exported Story Bible to {story_bible_path}")
        self.log_end(success=True)
        
        return {
            "success": True,
            "manuscript_path": manuscript_path,
            "story_bible_path": story_bible_path,
            "output_dir": self.output_dir
        }
        
    def _export_manuscript(self, bible: StoryBible) -> str:
        """
        Export manuscript to text file.
        
        Args:
            bible: Story Bible with manuscript
            
        Returns:
            Path to exported manuscript
        """
        manuscript_path = os.path.join(self.output_dir, "manuscript.txt")
        
        # Get compiled manuscript or compile on the fly
        if "manuscript_text" in bible.metadata:
            manuscript = bible.metadata["manuscript_text"]
        else:
            # Simple compilation if not already compiled
            manuscript = self._simple_compile(bible)
        
        with open(manuscript_path, "w", encoding="utf-8") as f:
            f.write(manuscript)
        
        return manuscript_path
        
    def _export_story_bible(self, bible: StoryBible) -> str:
        """
        Export Story Bible to JSON file.
        
        Args:
            bible: Story Bible to export
            
        Returns:
            Path to exported Story Bible
        """
        story_bible_path = os.path.join(self.output_dir, "story_bible.json")
        bible.save(Path(story_bible_path))
        return story_bible_path
        
    def _simple_compile(self, bible: StoryBible) -> str:
        """
        Simple manuscript compilation if not already compiled.
        
        Args:
            bible: Story Bible with chapters
            
        Returns:
            Compiled manuscript text
        """
        parts = []
        
        for chapter_num in sorted(bible.chapters.keys()):
            chapter = bible.chapters[chapter_num]
            if chapter.content:
                parts.append(chapter.content)
                parts.append("\n\n")
        
        return "".join(parts)

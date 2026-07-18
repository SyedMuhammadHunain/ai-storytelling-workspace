"""Compilation Agent - Assembles complete manuscript."""

from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible


class CompilationAgent(MockAgent):
    """
    Compilation Agent assembles the complete manuscript.
    
    Combines front matter, chapters, and back matter into final manuscript.
    """
    
    def __init__(self):
        """Initialize the Compilation Agent."""
        super().__init__(name="Compilation Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute manuscript compilation.
        
        Args:
            bible: Story Bible to compile from
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Compile manuscript
        manuscript = self._compile_manuscript(bible)
        
        # Store in metadata
        bible.metadata["compiled_manuscript"] = {
            "word_count": len(manuscript.split()),
            "compiled": True
        }
        
        # Store full manuscript (in production, might store reference instead)
        bible.metadata["manuscript_text"] = manuscript
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "compilation": True,
                "word_count": len(manuscript.split())
            },
            summary=f"Compiled manuscript: {len(manuscript.split())} words"
        )
        
        self.log_action(f"Compiled manuscript: {len(manuscript.split())} words")
        self.log_end(success=True)
        
        return {
            "success": True,
            "word_count": len(manuscript.split()),
            "manuscript": manuscript
        }
        
    def _compile_manuscript(self, bible: StoryBible) -> str:
        """
        Compile complete manuscript.
        
        Args:
            bible: Story Bible with all content
            
        Returns:
            Complete manuscript text
        """
        parts = []
        
        # Add front matter
        if "front_matter" in bible.metadata:
            front = bible.metadata["front_matter"]
            parts.append(front.get("title_page", ""))
            parts.append("\n\n")
            parts.append(front.get("copyright", ""))
            parts.append("\n\n")
            parts.append(front.get("table_of_contents", ""))
            parts.append("\n\n---\n\n")
        
        # Add chapters in order
        for chapter_num in sorted(bible.chapters.keys()):
            chapter = bible.chapters[chapter_num]
            if chapter.content:
                parts.append(chapter.content)
                parts.append("\n\n")
        
        # Add back matter
        if "back_matter" in bible.metadata:
            back = bible.metadata["back_matter"]
            parts.append("\n\n---\n\n")
            parts.append(back.get("acknowledgments", ""))
            parts.append("\n\n")
            parts.append(back.get("author_bio", ""))
        
        return "".join(parts)

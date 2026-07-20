"""Compilation Agent - Assembles complete manuscript."""

from typing import Dict, Any

from .base import BaseAgent
from ..story_bible import StoryBible


class CompilationAgent(BaseAgent):
    """
    Compilation Agent assembles the complete manuscript.
    
    Combines front matter, chapters, and back matter into final manuscript.
    This is primarily an assembly task, not requiring AI generation.
    """
    
    def __init__(self):
        """Initialize the Compilation Agent."""
        super().__init__(name="Compilation Agent")
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
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
        word_count = len(manuscript.split())
        
        # Store in metadata
        bible.metadata["compiled_manuscript"] = {
            "word_count": word_count,
            "compiled": True,
            "sections": self._count_sections(bible)
        }
        
        # Store full manuscript (in production, might store reference instead)
        bible.metadata["manuscript_text"] = manuscript
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "compilation": True,
                "word_count": word_count
            },
            summary=f"Compiled manuscript: {word_count} words"
        )
        
        self.log_action(f"Compiled manuscript: {word_count} words")
        self.log_end(success=True)
        
        return {
            "success": True,
            "word_count": word_count,
            "manuscript": manuscript,
            "sections": self._count_sections(bible)
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
            
            if "title_page" in front:
                parts.append(front["title_page"])
                parts.append("\n\n" + "="*50 + "\n\n")
            
            if "copyright" in front:
                parts.append(front["copyright"])
                parts.append("\n\n" + "="*50 + "\n\n")
            
            if "dedication" in front:
                parts.append(front["dedication"])
                parts.append("\n\n" + "="*50 + "\n\n")
            
            if "table_of_contents" in front:
                parts.append(front["table_of_contents"])
                parts.append("\n\n" + "="*50 + "\n\n")
        
        # Add chapters in order
        for chapter in sorted(bible.chapters, key=lambda c: c.number):
            if chapter.content:
                parts.append(f"\n\n# Chapter {chapter.number}: {chapter.title}\n\n")
                parts.append(chapter.content)
                parts.append("\n\n" + "-"*50 + "\n\n")
        
        # Add back matter
        if "back_matter" in bible.metadata:
            back = bible.metadata["back_matter"]
            
            parts.append("\n\n" + "="*50 + "\n\n")
            
            if "acknowledgments" in back:
                parts.append(back["acknowledgments"])
                parts.append("\n\n" + "="*50 + "\n\n")
            
            if "author_bio" in back:
                parts.append(back["author_bio"])
                parts.append("\n\n")
            
            if "discussion_questions" in back:
                parts.append(back["discussion_questions"])
                parts.append("\n\n")
        
        return "".join(parts)
    
    def _count_sections(self, bible: StoryBible) -> Dict[str, int]:
        """
        Count sections in the manuscript.
        
        Args:
            bible: Story Bible
            
        Returns:
            Dictionary with section counts
        """
        return {
            "front_matter_sections": len(bible.metadata.get("front_matter", {})),
            "chapters": len(bible.chapters),
            "back_matter_sections": len(bible.metadata.get("back_matter", {}))
        }
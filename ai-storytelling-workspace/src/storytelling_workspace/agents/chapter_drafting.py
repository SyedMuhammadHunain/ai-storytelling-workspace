"""Chapter Drafting Agent - Generates chapter content."""

from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible


class ChapterDraftingAgent(MockAgent):
    """
    Chapter Drafting Agent generates chapter content.
    
    In MVP, generates simple mock text. Designed to be instantiated
    multiple times for parallel execution.
    """
    
    def __init__(self, chapter_number: int):
        """
        Initialize the Chapter Drafting Agent.
        
        Args:
            chapter_number: The chapter number to draft
        """
        super().__init__(name=f"Chapter Drafting Agent (Ch. {chapter_number})")
        self.chapter_number = chapter_number
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute chapter drafting.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Get chapter outline
        chapter = bible.get_chapter(self.chapter_number)
        if not chapter:
            self.log_end(success=False)
            return {
                "success": False,
                "error": f"Chapter {self.chapter_number} not found in outline"
            }
        
        # Generate mock chapter content
        content = self._generate_mock_content(chapter.title, chapter.pov, chapter.goal)
        
        # Update chapter with content
        chapter.content = content
        chapter.status = "drafted"
        bible.add_chapter(chapter)  # Update in Story Bible
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "chapter": self.chapter_number,
                "word_count": len(content.split()),
                "status": "drafted"
            },
            summary=f"Drafted Chapter {self.chapter_number}: {chapter.title}"
        )
        
        self.log_action(f"Drafted chapter {self.chapter_number} ({len(content.split())} words)")
        self.log_end(success=True)
        
        return {
            "success": True,
            "chapter_number": self.chapter_number,
            "word_count": len(content.split())
        }
        
    def _generate_mock_content(self, title: str, pov: str, goal: str) -> str:
        """Generate mock chapter content for MVP."""
        return f"""# Chapter {self.chapter_number}: {title}

[Mock chapter content - POV: {pov}]

This chapter focuses on: {goal}

The story unfolds as our protagonist faces new challenges and discoveries. 
Through trials and tribulations, character development occurs naturally.
The plot advances toward its inevitable conclusion.

Key scenes in this chapter:
- Opening scene establishing the chapter's tone
- Character interactions revealing motivations
- Rising tension building toward the chapter's climax
- Resolution that sets up the next chapter

[End of mock content for Chapter {self.chapter_number}]

Word count: ~150 words (mock)
"""

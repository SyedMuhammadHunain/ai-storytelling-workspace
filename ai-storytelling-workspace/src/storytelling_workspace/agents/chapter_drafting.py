"""Chapter Drafting Agent - Generates chapter content."""

import asyncio
from typing import Dict, Any

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class ChapterDraftingAgent(AIAgent):
    """
    Chapter Drafting Agent generates chapter content using AI.
    
    Designed to be instantiated multiple times for parallel execution.
    Each instance handles one chapter.
    """
    
    def __init__(self, chapter_number: int, ai_provider=None):
        """
        Initialize the Chapter Drafting Agent.
        
        Args:
            chapter_number: The chapter number to draft
            ai_provider: Optional AI provider factory
        """
        super().__init__(
            name=f"Chapter Drafting Agent (Ch. {chapter_number})",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.8,  # Higher temperature for creative writing
            default_max_tokens=4000  # Longer for chapter content
        )
        self.chapter_number = chapter_number
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
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
        
        # Generate chapter content with AI
        content = await self._generate_chapter_content(bible, chapter)
        
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
    
    async def _generate_chapter_content(self, bible: StoryBible, chapter) -> str:
        """
        Generate chapter content using AI.
        
        Args:
            bible: Story Bible with context
            chapter: Chapter object with outline
            
        Returns:
            Generated chapter content
        """
        # Prepare context
        chapter_outline = self._prepare_chapter_outline(chapter)
        previous_summary = self._get_previous_chapter_summary(bible, chapter.number)
        pov_character = self._get_character_info(bible, chapter.pov)
        
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.CHAPTER_DRAFT,
            chapter_number=chapter.number,
            chapter_title=chapter.title,
            genre=bible.brief.genre,
            tone=bible.brief.tone,
            pov_character=pov_character,
            setting=getattr(chapter, 'setting', 'To be determined'),
            chapter_outline=chapter_outline,
            previous_chapter_summary=previous_summary,
            target_words=chapter.word_count_target
        )
        
        # Generate chapter with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.8,
            max_tokens=4000
        )
        
        return response.content
    
    def _prepare_chapter_outline(self, chapter) -> str:
        """
        Prepare chapter outline for prompt.
        
        Args:
            chapter: Chapter object
            
        Returns:
            Formatted outline string
        """
        outline_parts = []
        
        if chapter.goal:
            outline_parts.append(f"Goal: {chapter.goal}")
        
        if chapter.conflict:
            outline_parts.append(f"Conflict: {chapter.conflict}")
        
        # Add plot points if available
        if hasattr(chapter, 'plot_points') and chapter.plot_points:
            outline_parts.append("Key Events:")
            for point in chapter.plot_points:
                outline_parts.append(f"- {point}")
        
        return "\n".join(outline_parts) if outline_parts else "Chapter outline to be determined"
    
    def _get_previous_chapter_summary(self, bible: StoryBible, current_chapter_num: int) -> str:
        """
        Get summary of previous chapter for continuity.
        
        Args:
            bible: Story Bible
            current_chapter_num: Current chapter number
            
        Returns:
            Previous chapter summary
        """
        if current_chapter_num <= 1:
            return "This is the first chapter."
        
        prev_chapter = bible.get_chapter(current_chapter_num - 1)
        if not prev_chapter:
            return "Previous chapter not available."
        
        # If previous chapter has content, create a brief summary
        if prev_chapter.content:
            # Take first 200 words as summary
            words = prev_chapter.content.split()[:200]
            return " ".join(words) + "..."
        
        # Otherwise use the outline
        return f"Previous chapter ({prev_chapter.title}): {prev_chapter.goal}"
    
    def _get_character_info(self, bible: StoryBible, character_name: str) -> str:
        """
        Get character information for POV context.
        
        Args:
            bible: Story Bible
            character_name: Name of POV character
            
        Returns:
            Character information string
        """
        # Find character in bible
        for char in bible.characters.values():
            if char.name.lower() == character_name.lower():
                info_parts = [
                    f"Name: {char.name}",
                    f"Role: {char.role}",
                ]
                
                if char.voice_signature:
                    info_parts.append(f"Voice: {char.voice_signature}")
                
                if char.goals:
                    info_parts.append(f"Goals: {', '.join(char.goals[:2])}")
                
                return "\n".join(info_parts)
        
        return f"Character: {character_name} (details to be determined)"
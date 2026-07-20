"""Copy Editor Agent - Reviews grammar, punctuation, and formatting."""

import asyncio
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class CopyEditorAgent(AIAgent):
    """
    Copy Editor Agent reviews technical correctness using AI.
    
    Focuses on grammar, punctuation, tense consistency, and formatting rules.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Copy Editor Agent."""
        super().__init__(
            name="Copy Editor Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.2,  # Very low temperature for precise corrections
            default_max_tokens=2500
        )
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute copy editing.
        
        Args:
            bible: Story Bible to edit
            
        Returns:
            Execution results with copy edit corrections
        """
        self.log_start()
        
        # Perform AI-powered copy editing
        corrections = await self._perform_copy_editing(bible)
        
        # Store report in metadata
        if "copy_edit_reports" not in bible.metadata:
            bible.metadata["copy_edit_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "corrections": corrections,
            "total_corrections": sum(len(c.get('errors', [])) for c in corrections)
        }
        
        bible.metadata["copy_edit_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "copy_edit": True,
                "chapters_reviewed": len(corrections)
            },
            summary=f"Copy edit complete: {len(corrections)} chapters reviewed"
        )
        
        self.log_action(f"Copy edit: {len(corrections)} chapters reviewed")
        self.log_end(success=True)
        
        return {
            "success": True,
            "corrections": corrections,
            "report": report
        }
    
    async def _perform_copy_editing(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Perform copy editing using AI.
        
        Args:
            bible: Story Bible with chapters
            
        Returns:
            List of correction reports per chapter
        """
        corrections = []
        
        # Review chapters with content
        for chapter in bible.chapters:
            if not chapter.content or len(chapter.content) < 100:
                continue
            
            # Take sample text from chapter (first 1500 chars)
            sample_text = chapter.content[:1500]
            
            # Format prompt
            prompt = PromptTemplates.format_prompt(
                PromptTemplates.COPY_EDIT,
                text=sample_text
            )
            
            # Generate copy edits with AI
            response = await self.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=2000
            )
            
            # Parse corrections
            chapter_corrections = self._parse_copy_corrections(response.content)
            
            if chapter_corrections:
                corrections.append({
                    "chapter": chapter.number,
                    "title": chapter.title,
                    "errors": chapter_corrections
                })
            
            # Limit to first 5 chapters for efficiency
            if len(corrections) >= 5:
                break
        
        return corrections
    
    def _parse_copy_corrections(self, ai_response: str) -> List[Dict[str, str]]:
        """
        Parse AI response into copy corrections.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            List of correction dictionaries
        """
        corrections = []
        
        # Check if AI says text is clean
        if 'no errors' in ai_response.lower() or 'clean' in ai_response.lower():
            return []
        
        lines = ai_response.strip().split('\n')
        current_correction = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect correction sections
            if 'location:' in line.lower():
                if current_correction and 'error_type' in current_correction:
                    corrections.append(current_correction)
                current_correction = {
                    'location': line.split(':', 1)[1].strip()
                }
            elif 'error' in line.lower() and 'type' in line.lower():
                if current_correction:
                    current_correction['error_type'] = line.split(':', 1)[1].strip()
            elif 'current:' in line.lower() or 'incorrect:' in line.lower():
                if current_correction:
                    current_correction['current'] = line.split(':', 1)[1].strip()
            elif 'correction:' in line.lower() or 'correct:' in line.lower():
                if current_correction:
                    current_correction['correction'] = line.split(':', 1)[1].strip()
            elif 'explanation:' in line.lower():
                if current_correction:
                    current_correction['explanation'] = line.split(':', 1)[1].strip()
        
        # Save last correction
        if current_correction and 'error_type' in current_correction:
            corrections.append(current_correction)
        
        return corrections
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
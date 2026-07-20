"""Line Editor Agent - Reviews prose rhythm and word choice."""

import asyncio
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class LineEditorAgent(AIAgent):
    """
    Line Editor Agent reviews prose at the sentence level using AI.
    
    Focuses on rhythm, word choice, clarity, and redundancy.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Line Editor Agent."""
        super().__init__(
            name="Line Editor Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.4,  # Lower temperature for precise editing
            default_max_tokens=3000
        )
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute line editing.
        
        Args:
            bible: Story Bible to edit
            
        Returns:
            Execution results with line edit suggestions
        """
        self.log_start()
        
        # Perform AI-powered line editing
        edits = await self._perform_line_editing(bible)
        
        # Store report in metadata
        if "line_edit_reports" not in bible.metadata:
            bible.metadata["line_edit_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "edits": edits,
            "total_edits": sum(len(e.get('suggestions', [])) for e in edits)
        }
        
        bible.metadata["line_edit_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "line_edit": True,
                "chapters_edited": len(edits)
            },
            summary=f"Line edit complete: {len(edits)} chapters reviewed"
        )
        
        self.log_action(f"Line edit: {len(edits)} chapters reviewed")
        self.log_end(success=True)
        
        return {
            "success": True,
            "edits": edits,
            "report": report
        }
    
    async def _perform_line_editing(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Perform line editing using AI.
        
        Args:
            bible: Story Bible with chapters
            
        Returns:
            List of edit reports per chapter
        """
        edits = []
        
        # Review chapters with content
        for chapter in bible.chapters:
            if not chapter.content or len(chapter.content) < 100:
                continue
            
            # Take sample text from chapter (first 1500 chars)
            sample_text = chapter.content[:1500]
            
            # Format prompt
            prompt = PromptTemplates.format_prompt(
                PromptTemplates.LINE_EDIT,
                text=sample_text
            )
            
            # Generate line edits with AI
            response = await self.generate_text(
                prompt=prompt,
                temperature=0.4,
                max_tokens=2000
            )
            
            # Parse edits
            chapter_edits = self._parse_line_edits(response.content)
            
            if chapter_edits:
                edits.append({
                    "chapter": chapter.number,
                    "title": chapter.title,
                    "suggestions": chapter_edits
                })
            
            # Limit to first 5 chapters for efficiency
            if len(edits) >= 5:
                break
        
        return edits
    
    def _parse_line_edits(self, ai_response: str) -> List[Dict[str, str]]:
        """
        Parse AI response into line edits.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            List of edit dictionaries
        """
        edits = []
        
        # Check if AI says text is clean
        if 'no changes' in ai_response.lower() or 'looks good' in ai_response.lower():
            return []
        
        lines = ai_response.strip().split('\n')
        current_edit = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect edit sections
            if 'before:' in line.lower() or 'original:' in line.lower():
                if current_edit and 'before' in current_edit:
                    edits.append(current_edit)
                current_edit = {
                    'before': line.split(':', 1)[1].strip()
                }
            elif 'after:' in line.lower() or 'edited:' in line.lower():
                if current_edit:
                    current_edit['after'] = line.split(':', 1)[1].strip()
            elif 'reason:' in line.lower() or 'explanation:' in line.lower():
                if current_edit:
                    current_edit['reason'] = line.split(':', 1)[1].strip()
        
        # Save last edit
        if current_edit and 'before' in current_edit:
            edits.append(current_edit)
        
        return edits
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
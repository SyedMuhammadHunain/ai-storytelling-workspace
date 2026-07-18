"""Line Editor Agent - Reviews prose rhythm and word choice."""

from typing import Dict, Any, List

from .base import MockAgent
from ..story_bible import StoryBible


class LineEditorAgent(MockAgent):
    """
    Line Editor Agent reviews prose at the sentence level.
    
    Focuses on rhythm, word choice, clarity, and redundancy.
    """
    
    def __init__(self):
        """Initialize the Line Editor Agent."""
        super().__init__(name="Line Editor Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute line editing.
        
        Args:
            bible: Story Bible to edit
            
        Returns:
            Execution results with line edit suggestions
        """
        self.log_start()
        
        # Perform mock line editing
        suggestions = self._generate_line_edit_suggestions(bible)
        
        # Store report in metadata
        if "line_edit_reports" not in bible.metadata:
            bible.metadata["line_edit_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
        
        bible.metadata["line_edit_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "line_edit": True,
                "suggestions": len(suggestions)
            },
            summary=f"Line edit complete: {len(suggestions)} suggestions"
        )
        
        self.log_action(f"Line edit: {len(suggestions)} suggestions")
        self.log_end(success=True)
        
        return {
            "success": True,
            "suggestions": suggestions,
            "report": report
        }
        
    def _generate_line_edit_suggestions(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Generate mock line edit suggestions.
        
        Args:
            bible: Story Bible to edit
            
        Returns:
            List of line edit suggestions
        """
        suggestions = []
        
        if len(bible.chapters) > 0:
            suggestions.append({
                "type": "word_choice",
                "chapter": 1,
                "description": "Consider stronger verb choices in action sequences",
                "example": "Replace 'walked quickly' with 'strode' or 'hurried'"
            })
            
            suggestions.append({
                "type": "rhythm",
                "chapter": 3,
                "description": "Vary sentence length for better pacing",
                "example": "Mix short, punchy sentences with longer, flowing ones"
            })
            
            suggestions.append({
                "type": "clarity",
                "chapter": 5,
                "description": "Simplify complex sentences for clarity",
                "example": "Break compound sentences into simpler structures"
            })
        
        return suggestions
        
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

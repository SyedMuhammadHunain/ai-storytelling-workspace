"""Copy Editor Agent - Reviews grammar, punctuation, and formatting."""

from typing import Dict, Any, List

from .base import MockAgent
from ..story_bible import StoryBible


class CopyEditorAgent(MockAgent):
    """
    Copy Editor Agent reviews technical correctness.
    
    Focuses on grammar, punctuation, tense consistency, and formatting rules.
    """
    
    def __init__(self):
        """Initialize the Copy Editor Agent."""
        super().__init__(name="Copy Editor Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute copy editing.
        
        Args:
            bible: Story Bible to edit
            
        Returns:
            Execution results with copy edit corrections
        """
        self.log_start()
        
        # Perform mock copy editing
        corrections = self._generate_copy_edit_corrections(bible)
        
        # Store report in metadata
        if "copy_edit_reports" not in bible.metadata:
            bible.metadata["copy_edit_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "corrections": corrections,
            "total_corrections": len(corrections)
        }
        
        bible.metadata["copy_edit_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "copy_edit": True,
                "corrections": len(corrections)
            },
            summary=f"Copy edit complete: {len(corrections)} corrections"
        )
        
        self.log_action(f"Copy edit: {len(corrections)} corrections")
        self.log_end(success=True)
        
        return {
            "success": True,
            "corrections": corrections,
            "report": report
        }
        
    def _generate_copy_edit_corrections(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Generate mock copy edit corrections.
        
        Args:
            bible: Story Bible to edit
            
        Returns:
            List of copy edit corrections
        """
        corrections = []
        
        if len(bible.chapters) > 0:
            corrections.append({
                "type": "grammar",
                "chapter": 2,
                "description": "Subject-verb agreement issue",
                "correction": "Ensure plural subjects have plural verbs"
            })
            
            corrections.append({
                "type": "punctuation",
                "chapter": 4,
                "description": "Missing comma in compound sentence",
                "correction": "Add comma before coordinating conjunction"
            })
            
            corrections.append({
                "type": "tense_consistency",
                "chapter": 6,
                "description": "Tense shift from past to present",
                "correction": "Maintain consistent past tense throughout"
            })
            
            corrections.append({
                "type": "formatting",
                "chapter": 8,
                "description": "Inconsistent dialogue formatting",
                "correction": "Use consistent quotation mark style"
            })
        
        return corrections
        
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

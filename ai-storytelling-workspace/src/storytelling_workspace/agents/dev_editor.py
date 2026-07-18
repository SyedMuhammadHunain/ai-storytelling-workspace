"""Developmental Editor Agent - Evaluates story structure and pacing."""

from typing import Dict, Any, List

from .base import MockAgent
from ..story_bible import StoryBible


class DevelopmentalEditorAgent(MockAgent):
    """
    Developmental Editor Agent evaluates big-picture story elements.
    
    Reviews pacing, stakes, structure, character arcs, and plot coherence.
    """
    
    def __init__(self):
        """Initialize the Developmental Editor Agent."""
        super().__init__(name="Developmental Editor Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute developmental edit.
        
        Args:
            bible: Story Bible to evaluate
            
        Returns:
            Execution results with developmental notes
        """
        self.log_start()
        
        # Perform mock developmental analysis
        notes = self._generate_developmental_notes(bible)
        
        # Store report in metadata
        if "dev_edit_reports" not in bible.metadata:
            bible.metadata["dev_edit_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "notes": notes,
            "overall_assessment": "Strong foundation with minor pacing adjustments needed"
        }
        
        bible.metadata["dev_edit_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "dev_edit": True,
                "notes_count": len(notes)
            },
            summary=f"Developmental edit complete: {len(notes)} notes"
        )
        
        self.log_action(f"Developmental edit: {len(notes)} notes generated")
        self.log_end(success=True)
        
        return {
            "success": True,
            "notes": notes,
            "report": report
        }
        
    def _generate_developmental_notes(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Generate mock developmental notes.
        
        Args:
            bible: Story Bible to evaluate
            
        Returns:
            List of developmental notes
        """
        notes = []
        
        # Note 1: Pacing
        notes.append({
            "category": "pacing",
            "priority": "medium",
            "description": "Middle chapters (5-7) may benefit from tighter pacing",
            "suggestion": "Consider condensing exposition in Chapter 6 to maintain momentum",
            "chapters": [5, 6, 7]
        })
        
        # Note 2: Character arc
        if len(bible.characters) > 0:
            protagonist = [c for c in bible.characters.values() if c.role == "protagonist"]
            if protagonist:
                notes.append({
                    "category": "character_arc",
                    "priority": "low",
                    "description": f"{protagonist[0].name}'s transformation could be more gradual",
                    "suggestion": "Add smaller victories in early chapters to show incremental growth",
                    "chapters": [2, 3, 4]
                })
        
        # Note 3: Stakes
        notes.append({
            "category": "stakes",
            "priority": "high",
            "description": "Stakes could be clearer in the first act",
            "suggestion": "Establish what the protagonist stands to lose earlier in the narrative",
            "chapters": [1, 2]
        })
        
        return notes
        
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

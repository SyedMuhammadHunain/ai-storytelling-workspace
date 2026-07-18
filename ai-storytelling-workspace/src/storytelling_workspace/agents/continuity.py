"""Continuity Agent - Checks for contradictions and consistency."""

from typing import Dict, Any, List

from .base import MockAgent
from ..story_bible import StoryBible


class ContinuityAgent(MockAgent):
    """
    Continuity Agent checks for contradictions in the manuscript.
    
    Reviews timeline, character details, world rules, and plot threads
    for consistency issues.
    """
    
    def __init__(self):
        """Initialize the Continuity Agent."""
        super().__init__(name="Continuity Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute continuity check.
        
        Args:
            bible: Story Bible to check
            
        Returns:
            Execution results with continuity report
        """
        self.log_start()
        
        # Perform mock continuity checks
        issues = self._check_continuity(bible)
        
        # Store continuity report in metadata
        if "continuity_reports" not in bible.metadata:
            bible.metadata["continuity_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "issues_found": len(issues),
            "issues": issues,
            "status": "clean" if len(issues) == 0 else "issues_found"
        }
        
        bible.metadata["continuity_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "continuity_check": True,
                "issues_found": len(issues)
            },
            summary=f"Continuity check complete: {len(issues)} issues found"
        )
        
        self.log_action(f"Continuity check: {len(issues)} issues found")
        self.log_end(success=True)
        
        return {
            "success": True,
            "issues_found": len(issues),
            "issues": issues,
            "report": report
        }
        
    def _check_continuity(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Perform mock continuity checks.
        
        In MVP, generates 0-2 mock issues. In production, would perform
        actual analysis of the manuscript.
        
        Args:
            bible: Story Bible to check
            
        Returns:
            List of continuity issues found
        """
        issues = []
        
        # Mock issue 1: Character consistency (only if we have chapters)
        if len(bible.chapters) > 5:
            issues.append({
                "type": "character_consistency",
                "severity": "low",
                "description": "Character voice may drift in later chapters",
                "chapters": [6, 7, 8],
                "suggestion": "Review dialogue for consistency with established voice signature"
            })
        
        # Mock issue 2: Timeline (only if we have many timeline events)
        if len(bible.timeline) > 2:
            issues.append({
                "type": "timeline",
                "severity": "medium",
                "description": "Timeline reference in Chapter 4 may conflict with established history",
                "chapters": [4],
                "suggestion": "Verify dates align with timeline in Story Bible"
            })
        
        return issues
        
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

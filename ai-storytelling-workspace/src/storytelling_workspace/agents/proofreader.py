"""Proofreader Agent - Final surface-level check."""

from typing import Dict, Any, List

from .base import MockAgent
from ..story_bible import StoryBible


class ProofreaderAgent(MockAgent):
    """
    Proofreader Agent performs final surface-level checks.
    
    Focuses on typos, spacing, formatting, and final polish.
    """
    
    def __init__(self):
        """Initialize the Proofreader Agent."""
        super().__init__(name="Proofreader Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute proofreading.
        
        Args:
            bible: Story Bible to proofread
            
        Returns:
            Execution results with proofreading report
        """
        self.log_start()
        
        # Perform mock proofreading
        issues = self._find_proofreading_issues(bible)
        
        # Store report in metadata
        if "proofread_reports" not in bible.metadata:
            bible.metadata["proofread_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "issues": issues,
            "total_issues": len(issues),
            "status": "clean" if len(issues) == 0 else "minor_issues"
        }
        
        bible.metadata["proofread_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "proofread": True,
                "issues": len(issues)
            },
            summary=f"Proofreading complete: {len(issues)} issues found"
        )
        
        self.log_action(f"Proofreading: {len(issues)} issues found")
        self.log_end(success=True)
        
        return {
            "success": True,
            "issues": issues,
            "report": report
        }
        
    def _find_proofreading_issues(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Find mock proofreading issues.
        
        Args:
            bible: Story Bible to proofread
            
        Returns:
            List of proofreading issues
        """
        issues = []
        
        if len(bible.chapters) > 0:
            # Mock issue 1: Typo
            issues.append({
                "type": "typo",
                "chapter": 3,
                "description": "Possible typo: 'recieve' should be 'receive'",
                "severity": "minor"
            })
            
            # Mock issue 2: Spacing
            if len(bible.chapters) > 5:
                issues.append({
                    "type": "spacing",
                    "chapter": 7,
                    "description": "Extra space before punctuation",
                    "severity": "minor"
                })
        
        return issues
        
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

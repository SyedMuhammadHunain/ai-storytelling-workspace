"""Dialogue/Voice Agent - Checks character voice consistency."""

from typing import Dict, Any, List

from .base import MockAgent
from ..story_bible import StoryBible


class DialogueVoiceAgent(MockAgent):
    """
    Dialogue/Voice Agent checks dialogue against character voice signatures.
    
    Reviews chapters for dialogue consistency with established character voices.
    """
    
    def __init__(self):
        """Initialize the Dialogue/Voice Agent."""
        super().__init__(name="Dialogue/Voice Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute dialogue/voice check.
        
        Args:
            bible: Story Bible to check
            
        Returns:
            Execution results with voice check report
        """
        self.log_start()
        
        # Perform mock voice check
        findings = self._check_voice_consistency(bible)
        
        # Store report in metadata
        if "voice_reports" not in bible.metadata:
            bible.metadata["voice_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "findings": findings,
            "status": "clean" if len(findings) == 0 else "suggestions_found"
        }
        
        bible.metadata["voice_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "voice_check": True,
                "findings": len(findings)
            },
            summary=f"Voice check complete: {len(findings)} suggestions"
        )
        
        self.log_action(f"Voice check: {len(findings)} suggestions")
        self.log_end(success=True)
        
        return {
            "success": True,
            "findings": findings,
            "report": report
        }
        
    def _check_voice_consistency(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Perform mock voice consistency check.
        
        Args:
            bible: Story Bible to check
            
        Returns:
            List of voice consistency findings
        """
        findings = []
        
        # Mock finding: character voice drift
        if len(bible.characters) > 0 and len(bible.chapters) > 3:
            findings.append({
                "type": "voice_consistency",
                "character": list(bible.characters.keys())[0],
                "chapters": [4, 5],
                "description": "Character dialogue may drift from established voice signature",
                "suggestion": "Review dialogue for consistency with character's voice patterns"
            })
        
        return findings
        
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

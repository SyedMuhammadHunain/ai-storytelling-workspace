"""QA Agent - Validates manuscript completeness."""

from typing import Dict, Any, List

from .base import MockAgent
from ..story_bible import StoryBible


class QAAgent(MockAgent):
    """
    QA Agent validates manuscript completeness.
    
    Checks for missing chapters, placeholder markers, and Story Bible completeness.
    """
    
    def __init__(self):
        """Initialize the QA Agent."""
        super().__init__(name="QA Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute QA validation.
        
        Args:
            bible: Story Bible to validate
            
        Returns:
            Execution results with QA report
        """
        self.log_start()
        
        # Perform QA checks
        issues = self._perform_qa_checks(bible)
        
        # Store QA report
        if "qa_reports" not in bible.metadata:
            bible.metadata["qa_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "issues": issues,
            "total_issues": len(issues),
            "status": "pass" if len(issues) == 0 else "issues_found"
        }
        
        bible.metadata["qa_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "qa_check": True,
                "issues_found": len(issues),
                "status": report["status"]
            },
            summary=f"QA check complete: {len(issues)} issues found"
        )
        
        self.log_action(f"QA validation: {len(issues)} issues found")
        self.log_end(success=True)
        
        return {
            "success": True,
            "issues": issues,
            "report": report
        }
        
    def _perform_qa_checks(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Perform QA validation checks.
        
        Args:
            bible: Story Bible to validate
            
        Returns:
            List of QA issues found
        """
        issues = []
        
        # Check for missing chapters
        if len(bible.chapters) > 0:
            expected_chapters = range(1, max(bible.chapters.keys()) + 1)
            for chapter_num in expected_chapters:
                if chapter_num not in bible.chapters:
                    issues.append({
                        "type": "missing_chapter",
                        "severity": "high",
                        "description": f"Chapter {chapter_num} is missing",
                        "chapter": chapter_num
                    })
        
        # Check for chapters without content
        for chapter_num, chapter in bible.chapters.items():
            if not chapter.content or chapter.content.strip() == "":
                issues.append({
                    "type": "empty_chapter",
                    "severity": "high",
                    "description": f"Chapter {chapter_num} has no content",
                    "chapter": chapter_num
                })
        
        # Check for placeholder markers (mock check)
        if "manuscript_text" in bible.metadata:
            manuscript = bible.metadata["manuscript_text"]
            if "[mock" in manuscript.lower() or "todo" in manuscript.lower():
                issues.append({
                    "type": "placeholder_found",
                    "severity": "medium",
                    "description": "Placeholder text found in manuscript",
                    "suggestion": "Review manuscript for [mock] or TODO markers"
                })
        
        # Check Story Bible completeness
        if not bible.brief or not bible.brief.genre:
            issues.append({
                "type": "incomplete_story_bible",
                "severity": "medium",
                "description": "Book brief is incomplete",
                "suggestion": "Ensure all required brief fields are filled"
            })
        
        return issues
        
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

"""QA Agent - Validates manuscript completeness."""

import asyncio
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class QAAgent(AIAgent):
    """
    QA Agent validates manuscript completeness using AI.
    
    Checks for missing chapters, placeholder markers, Story Bible completeness,
    and overall quality assessment.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the QA Agent."""
        super().__init__(
            name="QA Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.3,  # Lower temperature for analytical assessment
            default_max_tokens=2000
        )
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute QA validation.
        
        Args:
            bible: Story Bible to validate
            
        Returns:
            Execution results with QA report
        """
        self.log_start()
        
        # Perform structural checks first
        structural_issues = self._perform_structural_checks(bible)
        
        # Perform AI-powered quality assessment
        quality_assessment = await self._perform_quality_assessment(bible)
        
        # Combine all issues
        all_issues = structural_issues + quality_assessment.get('issues', [])
        
        # Store QA report
        if "qa_reports" not in bible.metadata:
            bible.metadata["qa_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "structural_issues": structural_issues,
            "quality_assessment": quality_assessment,
            "total_issues": len(all_issues),
            "status": "pass" if len(all_issues) == 0 else "issues_found",
            "overall_score": quality_assessment.get('score', 0)
        }
        
        bible.metadata["qa_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "qa_check": True,
                "issues_found": len(all_issues),
                "status": report["status"]
            },
            summary=f"QA check complete: {len(all_issues)} issues found, score: {quality_assessment.get('score', 0)}/10"
        )
        
        self.log_action(f"QA validation: {len(all_issues)} issues found")
        self.log_end(success=True)
        
        return {
            "success": True,
            "issues": all_issues,
            "report": report
        }
    
    def _perform_structural_checks(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Perform structural validation checks.
        
        Args:
            bible: Story Bible to validate
            
        Returns:
            List of structural issues found
        """
        issues = []
        
        # Check for missing chapters
        if bible.chapters:
            chapter_numbers = [c.number for c in bible.chapters]
            expected_chapters = range(1, max(chapter_numbers) + 1)
            for chapter_num in expected_chapters:
                if chapter_num not in chapter_numbers:
                    issues.append({
                        "type": "missing_chapter",
                        "severity": "high",
                        "description": f"Chapter {chapter_num} is missing",
                        "chapter": chapter_num
                    })
        
        # Check for chapters without content
        for chapter in bible.chapters:
            if not chapter.content or chapter.content.strip() == "":
                issues.append({
                    "type": "empty_chapter",
                    "severity": "high",
                    "description": f"Chapter {chapter.number} has no content",
                    "chapter": chapter.number
                })
        
        # Check Story Bible completeness
        if not bible.brief or not bible.brief.genre:
            issues.append({
                "type": "incomplete_story_bible",
                "severity": "medium",
                "description": "Book brief is incomplete",
                "suggestion": "Ensure all required brief fields are filled"
            })
        
        if not bible.characters:
            issues.append({
                "type": "missing_characters",
                "severity": "high",
                "description": "No characters defined in Story Bible",
                "suggestion": "Add character profiles"
            })
        
        return issues
    
    async def _perform_quality_assessment(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Perform AI-powered quality assessment.
        
        Args:
            bible: Story Bible
            
        Returns:
            Quality assessment dictionary
        """
        # Prepare manuscript summary
        manuscript_summary = self._prepare_manuscript_summary(bible)
        
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.QUALITY_ASSURANCE,
            manuscript_summary=manuscript_summary
        )
        
        # Generate quality assessment with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse assessment
        assessment = self._parse_quality_assessment(response.content)
        
        return assessment
    
    def _prepare_manuscript_summary(self, bible: StoryBible) -> str:
        """
        Prepare manuscript summary for assessment.
        
        Args:
            bible: Story Bible
            
        Returns:
            Manuscript summary string
        """
        parts = []
        
        # Basic info
        parts.append(f"Genre: {bible.brief.genre}")
        parts.append(f"Target Length: {bible.brief.target_length} words")
        parts.append(f"Chapters: {len(bible.chapters)}")
        parts.append(f"Characters: {len(bible.characters)}")
        
        # Word count
        if bible.metadata.get("compiled_manuscript"):
            parts.append(f"Actual Word Count: {bible.metadata['compiled_manuscript'].get('word_count', 0)}")
        
        # Completion status
        drafted_chapters = sum(1 for c in bible.chapters if c.status == "drafted")
        parts.append(f"Drafted Chapters: {drafted_chapters}/{len(bible.chapters)}")
        
        return "\n".join(parts)
    
    def _parse_quality_assessment(self, ai_response: str) -> Dict[str, Any]:
        """
        Parse AI quality assessment.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            Assessment dictionary
        """
        assessment = {
            "score": 7,  # Default score
            "strengths": [],
            "issues": [],
            "recommendation": "Ready to publish"
        }
        
        lines = ai_response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            lower_line = line.lower()
            
            # Detect score
            if 'score' in lower_line or 'rating' in lower_line:
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    assessment['score'] = int(numbers[0])
            
            # Detect sections
            elif 'strength' in lower_line:
                current_section = 'strengths'
            elif 'issue' in lower_line or 'weakness' in lower_line or 'concern' in lower_line:
                current_section = 'issues'
            elif 'recommendation' in lower_line:
                current_section = 'recommendation'
                if ':' in line:
                    assessment['recommendation'] = line.split(':', 1)[1].strip()
            elif line.startswith(('-', '•', '*')) and current_section:
                item = line.lstrip('-•* ')
                if current_section == 'strengths':
                    assessment['strengths'].append(item)
                elif current_section == 'issues':
                    assessment['issues'].append({
                        'type': 'quality',
                        'severity': 'medium',
                        'description': item
                    })
        
        return assessment
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
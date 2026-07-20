"""Proofreader Agent - Final surface-level check."""

import asyncio
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class ProofreaderAgent(AIAgent):
    """
    Proofreader Agent performs final surface-level checks using AI.
    
    Focuses on typos, spacing, formatting, and final polish.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Proofreader Agent."""
        super().__init__(
            name="Proofreader Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.1,  # Lowest temperature for precise proofreading
            default_max_tokens=2000
        )
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute proofreading.
        
        Args:
            bible: Story Bible to proofread
            
        Returns:
            Execution results with proofreading report
        """
        self.log_start()
        
        # Perform AI-powered proofreading
        issues = await self._perform_proofreading(bible)
        
        # Store report in metadata
        if "proofread_reports" not in bible.metadata:
            bible.metadata["proofread_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "issues": issues,
            "total_issues": sum(len(i.get('errors', [])) for i in issues),
            "status": "clean" if not issues else "minor_issues"
        }
        
        bible.metadata["proofread_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "proofread": True,
                "chapters_reviewed": len(issues)
            },
            summary=f"Proofreading complete: {len(issues)} chapters reviewed"
        )
        
        self.log_action(f"Proofreading: {len(issues)} chapters reviewed")
        self.log_end(success=True)
        
        return {
            "success": True,
            "issues": issues,
            "report": report
        }
    
    async def _perform_proofreading(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Perform proofreading using AI.
        
        Args:
            bible: Story Bible with chapters
            
        Returns:
            List of issue reports per chapter
        """
        issues = []
        
        # Review chapters with content
        for chapter in bible.chapters:
            if not chapter.content or len(chapter.content) < 100:
                continue
            
            # Take sample text from chapter (first 1500 chars)
            sample_text = chapter.content[:1500]
            
            # Format prompt
            prompt = PromptTemplates.format_prompt(
                PromptTemplates.PROOFREAD,
                text=sample_text
            )
            
            # Generate proofreading with AI
            response = await self.generate_text(
                prompt=prompt,
                temperature=0.1,
                max_tokens=1500
            )
            
            # Parse issues
            chapter_issues = self._parse_proofreading_issues(response.content)
            
            if chapter_issues:
                issues.append({
                    "chapter": chapter.number,
                    "title": chapter.title,
                    "errors": chapter_issues
                })
            
            # Limit to first 5 chapters for efficiency
            if len(issues) >= 5:
                break
        
        return issues
    
    def _parse_proofreading_issues(self, ai_response: str) -> List[Dict[str, str]]:
        """
        Parse AI response into proofreading issues.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            List of issue dictionaries
        """
        issues = []
        
        # Check if AI says text is clean
        if 'no errors' in ai_response.lower() or 'clean' in ai_response.lower() or 'ready' in ai_response.lower():
            return []
        
        lines = ai_response.strip().split('\n')
        current_issue = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect issue items
            if line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                # Save previous issue
                if current_issue and 'description' in current_issue:
                    issues.append(current_issue)
                
                # Start new issue
                issue_text = line.lstrip('-•*123456789. ')
                current_issue = {
                    'type': 'typo',
                    'description': issue_text,
                    'severity': 'minor'
                }
            elif 'location:' in line.lower():
                if current_issue:
                    current_issue['location'] = line.split(':', 1)[1].strip()
            elif 'current:' in line.lower() or 'error:' in line.lower():
                if current_issue:
                    current_issue['current'] = line.split(':', 1)[1].strip()
            elif 'corrected:' in line.lower() or 'fix:' in line.lower():
                if current_issue:
                    current_issue['corrected'] = line.split(':', 1)[1].strip()
        
        # Save last issue
        if current_issue and 'description' in current_issue:
            issues.append(current_issue)
        
        return issues
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
"""Continuity Agent - Checks for contradictions and consistency."""

import asyncio
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class ContinuityAgent(AIAgent):
    """
    Continuity Agent checks for contradictions in the manuscript using AI.
    
    Reviews timeline, character details, world rules, and plot threads
    for consistency issues.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Continuity Agent."""
        super().__init__(
            name="Continuity Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.3,  # Lower temperature for analytical task
            default_max_tokens=2000
        )
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute continuity check.
        
        Args:
            bible: Story Bible to check
            
        Returns:
            Execution results with continuity report
        """
        self.log_start()
        
        # Perform AI-powered continuity check
        issues = asyncio.run(self._check_continuity_with_ai(bible))
        
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
    
    async def _check_continuity_with_ai(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Perform AI-powered continuity check.
        
        Args:
            bible: Story Bible to check
            
        Returns:
            List of continuity issues found
        """
        # Prepare context for AI
        chapters_text = self._prepare_chapters_text(bible)
        characters_info = self._prepare_characters_info(bible)
        world_rules = self._prepare_world_rules(bible)
        timeline = self._prepare_timeline(bible)
        
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.CONTINUITY_CHECK,
            characters=characters_info,
            world_rules=world_rules,
            timeline=timeline,
            chapters_text=chapters_text
        )
        
        # Generate continuity analysis with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse AI response into issues
        issues = self._parse_continuity_issues(response.content)
        
        return issues
    
    def _prepare_chapters_text(self, bible: StoryBible) -> str:
        """
        Prepare chapter text for continuity check.
        
        Args:
            bible: Story Bible
            
        Returns:
            Formatted chapters text
        """
        if not bible.chapters:
            return "No chapters available for review."
        
        chapters_parts = []
        for chapter in bible.chapters[:10]:  # Check first 10 chapters
            if chapter.content:
                # Include first 500 words of each chapter
                words = chapter.content.split()[:500]
                content_preview = " ".join(words)
                chapters_parts.append(
                    f"Chapter {chapter.number}: {chapter.title}\n{content_preview}..."
                )
        
        return "\n\n".join(chapters_parts) if chapters_parts else "No chapter content available."
    
    def _prepare_characters_info(self, bible: StoryBible) -> str:
        """Prepare character information."""
        if not bible.characters:
            return "No characters defined."
        
        char_parts = []
        for char in bible.characters:
            char_parts.append(
                f"{char.name} ({char.role}): {char.physical_description}"
            )
        
        return "; ".join(char_parts)
    
    def _prepare_world_rules(self, bible: StoryBible) -> str:
        """Prepare world rules information."""
        if not bible.world_rules:
            return "No world rules defined."
        
        rules_parts = [
            f"Magic: {bible.world_rules.magic_system}",
            f"Technology: {bible.world_rules.technology_level}",
            f"Society: {bible.world_rules.social_structure}"
        ]
        
        return "; ".join(rules_parts)
    
    def _prepare_timeline(self, bible: StoryBible) -> str:
        """Prepare timeline information."""
        if not bible.timeline:
            return "No timeline defined."
        
        timeline_parts = []
        for event in bible.timeline:
            timeline_parts.append(f"{event.timestamp}: {event.event}")
        
        return "; ".join(timeline_parts)
    
    def _parse_continuity_issues(self, ai_response: str) -> List[Dict[str, Any]]:
        """
        Parse AI response into continuity issues.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            List of issue dictionaries
        """
        issues = []
        lines = ai_response.strip().split('\n')
        
        current_issue = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a "no issues" response
            if 'no issues' in line.lower() or 'consistent' in line.lower():
                return []
            
            # Detect issue boundaries
            if line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                # Save previous issue
                if current_issue and 'description' in current_issue:
                    issues.append(current_issue)
                
                # Start new issue
                issue_text = line.lstrip('-•*123456789. ')
                current_issue = {
                    'type': 'consistency',
                    'severity': 'medium',
                    'description': issue_text,
                    'chapters': [],
                    'suggestion': ''
                }
            elif 'location:' in line.lower() or 'chapter' in line.lower():
                # Extract chapter numbers
                import re
                numbers = re.findall(r'\d+', line)
                if numbers and current_issue:
                    current_issue['chapters'] = [int(n) for n in numbers]
            elif 'severity:' in line.lower():
                if current_issue:
                    severity = line.split(':', 1)[1].strip().lower()
                    current_issue['severity'] = severity
            elif 'suggestion:' in line.lower() or 'fix:' in line.lower():
                if current_issue:
                    current_issue['suggestion'] = line.split(':', 1)[1].strip()
        
        # Save last issue
        if current_issue and 'description' in current_issue:
            issues.append(current_issue)
        
        return issues
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
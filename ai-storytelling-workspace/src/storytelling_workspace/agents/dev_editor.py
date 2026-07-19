"""Developmental Editor Agent - Evaluates story structure and pacing."""

import asyncio
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class DevelopmentalEditorAgent(AIAgent):
    """
    Developmental Editor Agent evaluates big-picture story elements using AI.
    
    Reviews pacing, stakes, structure, character arcs, and plot coherence.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Developmental Editor Agent."""
        super().__init__(
            name="Developmental Editor Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.5,  # Balanced for analytical + creative feedback
            default_max_tokens=3000
        )
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute developmental edit.
        
        Args:
            bible: Story Bible to evaluate
            
        Returns:
            Execution results with developmental notes
        """
        self.log_start()
        
        # Perform AI-powered developmental analysis
        notes = asyncio.run(self._generate_developmental_notes(bible))
        
        # Store report in metadata
        if "dev_edit_reports" not in bible.metadata:
            bible.metadata["dev_edit_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "notes": notes,
            "overall_assessment": self._generate_overall_assessment(notes)
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
    
    async def _generate_developmental_notes(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Generate developmental notes using AI.
        
        Args:
            bible: Story Bible to evaluate
            
        Returns:
            List of developmental notes
        """
        # Prepare manuscript summary
        manuscript_summary = self._prepare_manuscript_summary(bible)
        
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.DEVELOPMENTAL_EDIT,
            genre=bible.brief.genre,
            theme=bible.concept.theme,
            target_audience=bible.brief.audience,
            manuscript_text=manuscript_summary
        )
        
        # Generate developmental feedback with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.5,
            max_tokens=3000
        )
        
        # Parse AI response into structured notes
        notes = self._parse_developmental_notes(response.content)
        
        return notes
    
    def _prepare_manuscript_summary(self, bible: StoryBible) -> str:
        """
        Prepare manuscript summary for analysis.
        
        Args:
            bible: Story Bible
            
        Returns:
            Manuscript summary string
        """
        parts = []
        
        # Add story overview
        parts.append(f"Genre: {bible.brief.genre}")
        parts.append(f"Premise: {bible.brief.premise}")
        parts.append(f"Theme: {bible.concept.theme}")
        
        # Add chapter summaries
        if bible.chapters:
            parts.append(f"\nChapters ({len(bible.chapters)} total):")
            for chapter in bible.chapters[:10]:  # First 10 chapters
                parts.append(f"- Ch{chapter.number}: {chapter.title} - {chapter.goal}")
        
        # Add character info
        if bible.characters:
            parts.append(f"\nMain Characters:")
            for char in bible.characters[:3]:
                parts.append(f"- {char.name} ({char.role}): {char.arc}")
        
        return "\n".join(parts)
    
    def _parse_developmental_notes(self, ai_response: str) -> List[Dict[str, Any]]:
        """
        Parse AI response into developmental notes.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            List of note dictionaries
        """
        notes = []
        lines = ai_response.strip().split('\n')
        
        current_note = {}
        current_category = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Detect categories
            lower_line = line.lower()
            if any(cat in lower_line for cat in ['story structure', 'structure', 'plot']):
                current_category = 'structure'
            elif any(cat in lower_line for cat in ['character', 'arc']):
                current_category = 'character_arc'
            elif 'pacing' in lower_line:
                current_category = 'pacing'
            elif any(cat in lower_line for cat in ['theme', 'message']):
                current_category = 'theme'
            elif any(cat in lower_line for cat in ['conflict', 'stakes', 'tension']):
                current_category = 'stakes'
            elif 'emotional' in lower_line or 'impact' in lower_line:
                current_category = 'emotional_impact'
            
            # Detect note items
            if line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                # Save previous note
                if current_note and 'description' in current_note:
                    notes.append(current_note)
                
                # Start new note
                note_text = line.lstrip('-•*123456789. ')
                current_note = {
                    'category': current_category or 'general',
                    'priority': 'medium',
                    'description': note_text,
                    'suggestion': '',
                    'chapters': []
                }
            elif 'priority:' in lower_line or 'severity:' in lower_line:
                if current_note:
                    priority = line.split(':', 1)[1].strip().lower()
                    current_note['priority'] = priority
            elif 'suggestion:' in lower_line or 'recommendation:' in lower_line:
                if current_note:
                    current_note['suggestion'] = line.split(':', 1)[1].strip()
            elif 'chapter' in lower_line and any(char.isdigit() for char in line):
                if current_note:
                    import re
                    numbers = re.findall(r'\d+', line)
                    current_note['chapters'] = [int(n) for n in numbers]
        
        # Save last note
        if current_note and 'description' in current_note:
            notes.append(current_note)
        
        # Ensure we have at least some notes
        if not notes:
            notes = self._create_default_notes()
        
        return notes
    
    def _create_default_notes(self) -> List[Dict[str, Any]]:
        """Create default notes as fallback."""
        return [
            {
                'category': 'structure',
                'priority': 'medium',
                'description': 'Story structure follows genre conventions',
                'suggestion': 'Continue with current approach',
                'chapters': []
            }
        ]
    
    def _generate_overall_assessment(self, notes: List[Dict[str, Any]]) -> str:
        """
        Generate overall assessment from notes.
        
        Args:
            notes: List of developmental notes
            
        Returns:
            Overall assessment string
        """
        if not notes:
            return "Manuscript shows strong foundation"
        
        high_priority = sum(1 for n in notes if n.get('priority') == 'high')
        
        if high_priority > 2:
            return "Significant structural revisions recommended"
        elif high_priority > 0:
            return "Strong foundation with some key areas for improvement"
        else:
            return "Solid manuscript with minor refinements suggested"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
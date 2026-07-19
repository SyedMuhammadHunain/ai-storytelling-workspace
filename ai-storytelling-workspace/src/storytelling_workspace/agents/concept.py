"""Concept Agent - Expands brief into full concept."""

import asyncio
from typing import Dict, Any

from .base import AIAgent
from ..story_bible import StoryBible
from ..models import Concept
from ..utils.prompts import PromptTemplates


class ConceptAgent(AIAgent):
    """
    Concept Agent expands the book brief into a full concept.
    
    Generates logline, premise, central conflict, and theme using AI.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Concept Agent."""
        super().__init__(
            name="Concept Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.7,
            default_max_tokens=1500
        )
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute concept development.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Run async generation in sync context
        concept = asyncio.run(self._generate_concept(bible))
        
        # Update Story Bible
        bible.concept = concept
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "concept": {
                    "logline": concept.logline,
                    "theme": concept.theme,
                    "central_conflict": concept.central_conflict
                }
            },
            summary=f"Developed concept with theme: {concept.theme}"
        )
        
        self.log_action(f"Created concept: {concept.logline}")
        self.log_end(success=True)
        
        return {
            "success": True,
            "concept": concept.to_dict()
        }
    
    async def _generate_concept(self, bible: StoryBible) -> Concept:
        """
        Generate concept using AI.
        
        Args:
            bible: Story Bible with brief information
            
        Returns:
            Generated Concept
        """
        # Format prompt with brief information
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.CONCEPT_DEVELOPMENT,
            genre=bible.brief.genre,
            premise=bible.brief.premise,
            tone=bible.brief.tone
        )
        
        # Generate concept with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse AI response into Concept object
        concept = self._parse_concept_response(response.content, bible.brief.premise)
        
        return concept
    
    def _parse_concept_response(self, ai_response: str, premise: str) -> Concept:
        """
        Parse AI response into Concept object.
        
        Args:
            ai_response: Raw AI response text
            premise: Original premise from brief
            
        Returns:
            Concept object
        """
        # Extract sections from AI response
        lines = ai_response.strip().split('\n')
        
        logline = ""
        central_conflict = ""
        theme = ""
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # Detect section headers
            if 'logline' in line.lower() and ':' in line:
                if current_section and current_content:
                    self._save_section(current_section, current_content, locals())
                current_section = 'logline'
                current_content = []
                # Check if content is on same line
                if line.split(':', 1)[1].strip():
                    current_content.append(line.split(':', 1)[1].strip())
            elif 'central conflict' in line.lower() and ':' in line:
                if current_section and current_content:
                    self._save_section(current_section, current_content, locals())
                current_section = 'central_conflict'
                current_content = []
                if line.split(':', 1)[1].strip():
                    current_content.append(line.split(':', 1)[1].strip())
            elif 'theme' in line.lower() and ':' in line:
                if current_section and current_content:
                    self._save_section(current_section, current_content, locals())
                current_section = 'theme'
                current_content = []
                if line.split(':', 1)[1].strip():
                    current_content.append(line.split(':', 1)[1].strip())
            elif line and current_section:
                # Skip markdown formatting and section markers
                if not line.startswith('#') and not line.startswith('**'):
                    current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            self._save_section(current_section, current_content, locals())
        
        # Extract values from locals
        logline = locals().get('logline', '')
        central_conflict = locals().get('central_conflict', '')
        theme = locals().get('theme', '')
        
        # Fallback to simple extraction if parsing failed
        if not logline:
            logline = self._extract_first_sentence(ai_response)
        if not central_conflict:
            central_conflict = "The protagonist must overcome challenges to achieve their goal."
        if not theme:
            theme = "Growth and transformation through adversity"
        
        return Concept(
            logline=logline,
            premise=premise,
            central_conflict=central_conflict,
            theme=theme
        )
    
    def _save_section(self, section: str, content: list, variables: dict) -> None:
        """Save parsed section content to variables."""
        text = ' '.join(content).strip()
        variables[section] = text
    
    def _extract_first_sentence(self, text: str) -> str:
        """Extract first meaningful sentence from text."""
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and not sentence.startswith('#'):
                return sentence + '.'
        return text[:200] + '...' if len(text) > 200 else text
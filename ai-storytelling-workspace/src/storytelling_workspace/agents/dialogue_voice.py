"""Dialogue/Voice Agent - Enhances dialogue and checks character voice consistency."""

import asyncio
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class DialogueVoiceAgent(AIAgent):
    """
    Dialogue/Voice Agent enhances dialogue and checks consistency with character voices.
    
    Uses AI to review and improve dialogue while maintaining character voice signatures.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Dialogue/Voice Agent."""
        super().__init__(
            name="Dialogue/Voice Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.7,
            default_max_tokens=3000
        )
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute dialogue/voice enhancement.
        
        Args:
            bible: Story Bible to check and enhance
            
        Returns:
            Execution results with voice check report
        """
        self.log_start()
        
        # Perform AI-powered dialogue enhancement
        enhancements = asyncio.run(self._enhance_dialogue(bible))
        
        # Store report in metadata
        if "voice_reports" not in bible.metadata:
            bible.metadata["voice_reports"] = []
        
        report = {
            "timestamp": self._get_timestamp(),
            "chapters_reviewed": len(enhancements),
            "enhancements": enhancements,
            "status": "complete"
        }
        
        bible.metadata["voice_reports"].append(report)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "voice_check": True,
                "chapters_enhanced": len(enhancements)
            },
            summary=f"Dialogue enhancement complete: {len(enhancements)} chapters reviewed"
        )
        
        self.log_action(f"Dialogue enhancement: {len(enhancements)} chapters reviewed")
        self.log_end(success=True)
        
        return {
            "success": True,
            "chapters_reviewed": len(enhancements),
            "enhancements": enhancements,
            "report": report
        }
    
    async def _enhance_dialogue(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """
        Enhance dialogue using AI.
        
        Args:
            bible: Story Bible with chapters
            
        Returns:
            List of enhancement reports per chapter
        """
        enhancements = []
        
        # Review chapters with content
        for chapter in bible.chapters:
            if not chapter.content or len(chapter.content) < 100:
                continue
            
            # Prepare context
            characters_present = self._identify_characters_in_chapter(bible, chapter)
            scene_context = f"{chapter.goal} - {chapter.conflict}"
            
            # Format prompt
            prompt = PromptTemplates.format_prompt(
                PromptTemplates.DIALOGUE_ENHANCEMENT,
                chapter_number=chapter.number,
                characters=", ".join(characters_present),
                scene_context=scene_context,
                chapter_text=chapter.content[:2000]  # First 2000 chars
            )
            
            # Generate dialogue analysis with AI
            response = await self.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse enhancements
            chapter_enhancements = self._parse_dialogue_enhancements(response.content)
            
            if chapter_enhancements:
                enhancements.append({
                    "chapter": chapter.number,
                    "title": chapter.title,
                    "enhancements": chapter_enhancements
                })
            
            # Limit to first 5 chapters for efficiency
            if len(enhancements) >= 5:
                break
        
        return enhancements
    
    def _identify_characters_in_chapter(self, bible: StoryBible, chapter) -> List[str]:
        """
        Identify which characters appear in a chapter.
        
        Args:
            bible: Story Bible
            chapter: Chapter to analyze
            
        Returns:
            List of character names
        """
        characters = []
        
        # Check POV character
        if chapter.pov:
            characters.append(chapter.pov)
        
        # Check for character names in content
        if chapter.content:
            for char in bible.characters:
                if char.name in chapter.content:
                    if char.name not in characters:
                        characters.append(char.name)
        
        return characters if characters else ["Unknown"]
    
    def _parse_dialogue_enhancements(self, ai_response: str) -> List[Dict[str, str]]:
        """
        Parse AI response into dialogue enhancements.
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            List of enhancement dictionaries
        """
        enhancements = []
        lines = ai_response.strip().split('\n')
        
        current_enhancement = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect enhancement sections
            if 'original' in line.lower() and ':' in line:
                if current_enhancement and 'original' in current_enhancement:
                    enhancements.append(current_enhancement)
                current_enhancement = {
                    'original': line.split(':', 1)[1].strip()
                }
            elif 'enhanced' in line.lower() and ':' in line:
                if current_enhancement:
                    current_enhancement['enhanced'] = line.split(':', 1)[1].strip()
            elif 'explanation' in line.lower() and ':' in line:
                if current_enhancement:
                    current_enhancement['explanation'] = line.split(':', 1)[1].strip()
        
        # Save last enhancement
        if current_enhancement and 'original' in current_enhancement:
            enhancements.append(current_enhancement)
        
        return enhancements
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
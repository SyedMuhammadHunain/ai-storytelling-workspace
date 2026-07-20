"""Plot Architect Agent - Creates chapter-by-chapter outline."""

import asyncio
from typing import Dict, Any, List

from .base import AIAgent
from ..story_bible import StoryBible
from ..models import Chapter, PlotThread
from ..utils.prompts import PromptTemplates


class PlotArchitectAgent(AIAgent):
    """
    Plot Architect Agent creates the story structure.
    
    Uses AI to generate chapter-by-chapter outline with act breaks, POV,
    goals, conflicts, and pacing.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Plot Architect Agent."""
        super().__init__(
            name="Plot Architect Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.7,
            default_max_tokens=4000
        )
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute plot architecture.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Generate plot structure with AI
        plot_data = await self._generate_plot_structure(bible)
        
        # Add chapters to Story Bible
        for chapter in plot_data["chapters"]:
            bible.add_chapter(chapter)
            
        # Add plot threads to Story Bible
        for thread in plot_data["plot_threads"]:
            bible.add_plot_thread(thread)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "chapters": len(plot_data["chapters"]),
                "plot_threads": len(plot_data["plot_threads"])
            },
            summary=f"Created outline with {len(plot_data['chapters'])} chapters and {len(plot_data['plot_threads'])} plot threads"
        )
        
        self.log_action(f"Created {len(plot_data['chapters'])} chapter outline")
        self.log_end(success=True)
        
        return {
            "success": True,
            "chapters_count": len(plot_data["chapters"]),
            "plot_threads_count": len(plot_data["plot_threads"])
        }
    
    async def _generate_plot_structure(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Generate plot structure using AI.
        
        Args:
            bible: Story Bible with story context
            
        Returns:
            Dictionary with chapters and plot_threads
        """
        # Calculate number of chapters based on target length
        target_words = bible.brief.target_length
        words_per_chapter = 8000
        num_chapters = max(10, min(30, target_words // words_per_chapter))
        
        # Prepare character summary
        character_summary = self._prepare_character_summary(bible)
        
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.PLOT_STRUCTURE,
            genre=bible.brief.genre,
            logline=bible.concept.logline,
            central_conflict=bible.concept.central_conflict,
            character_summary=character_summary,
            num_chapters=num_chapters
        )
        
        # Generate plot structure with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        # Parse AI response
        plot_data = self._parse_plot_response(response.content, num_chapters)
        
        return plot_data
    
    def _prepare_character_summary(self, bible: StoryBible) -> str:
        """
        Prepare character summary for plot context.
        
        Args:
            bible: Story Bible
            
        Returns:
            Character summary string
        """
        if not bible.characters:
            return "Characters to be determined"
        
        summaries = []
        for char in bible.characters[:5]:  # Top 5 characters
            summary = f"{char.name} ({char.role})"
            if char.goals:
                summary += f": {char.goals[0]}"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _parse_plot_response(self, ai_response: str, expected_chapters: int) -> Dict[str, Any]:
        """
        Parse AI response into chapters and plot threads.
        
        Args:
            ai_response: Raw AI response text
            expected_chapters: Expected number of chapters
            
        Returns:
            Dictionary with chapters and plot_threads
        """
        chapters = []
        plot_threads = []
        
        lines = ai_response.strip().split('\n')
        
        current_chapter = {}
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Detect chapter boundaries
            if 'chapter' in line.lower() and any(char.isdigit() for char in line):
                # Save previous chapter
                if current_chapter and 'number' in current_chapter:
                    chapters.append(self._create_chapter_from_dict(current_chapter))
                
                # Extract chapter number
                import re
                numbers = re.findall(r'\d+', line)
                chapter_num = int(numbers[0]) if numbers else len(chapters) + 1
                
                # Extract title if present
                title = ""
                if ':' in line:
                    title = line.split(':', 1)[1].strip()
                elif '"' in line:
                    title = line.split('"')[1] if len(line.split('"')) > 1 else ""
                
                current_chapter = {
                    'number': chapter_num,
                    'title': title or f"Chapter {chapter_num}"
                }
                current_section = None
                continue
            
            # Detect fields
            lower_line = line.lower()
            if 'title:' in lower_line and 'number' in current_chapter:
                current_chapter['title'] = line.split(':', 1)[1].strip()
            elif 'pov' in lower_line and ':' in line:
                current_chapter['pov'] = line.split(':', 1)[1].strip()
            elif 'setting:' in lower_line:
                current_chapter['setting'] = line.split(':', 1)[1].strip()
            elif 'goal' in lower_line and ':' in line:
                current_chapter['goal'] = line.split(':', 1)[1].strip()
            elif 'conflict' in lower_line and ':' in line:
                current_chapter['conflict'] = line.split(':', 1)[1].strip()
            elif 'plot' in lower_line and 'point' in lower_line:
                current_section = 'plot_points'
                if 'plot_points' not in current_chapter:
                    current_chapter['plot_points'] = []
            elif current_section == 'plot_points' and line.startswith(('-', '•', '*')):
                current_chapter['plot_points'].append(line.lstrip('-•* '))
        
        # Save last chapter
        if current_chapter and 'number' in current_chapter:
            chapters.append(self._create_chapter_from_dict(current_chapter))
        
        # Ensure we have the expected number of chapters
        if len(chapters) < expected_chapters:
            chapters.extend(self._create_default_chapters(
                start_num=len(chapters) + 1,
                count=expected_chapters - len(chapters)
            ))
        
        # Create default plot threads
        plot_threads = self._create_default_plot_threads(len(chapters))
        
        return {
            "chapters": chapters,
            "plot_threads": plot_threads
        }
    
    def _create_chapter_from_dict(self, chapter_dict: Dict[str, Any]) -> Chapter:
        """
        Create Chapter object from parsed dictionary.
        
        Args:
            chapter_dict: Dictionary with chapter data
            
        Returns:
            Chapter object
        """
        return Chapter(
            number=chapter_dict.get('number', 1),
            title=chapter_dict.get('title', f"Chapter {chapter_dict.get('number', 1)}"),
            pov=chapter_dict.get('pov', 'To be determined'),
            goal=chapter_dict.get('goal', 'Chapter goal to be determined'),
            conflict=chapter_dict.get('conflict', 'Conflict to be determined'),
            word_count_target=8000,
            status="planned"
        )
    
    def _create_default_chapters(self, start_num: int, count: int) -> List[Chapter]:
        """
        Create default chapters as fallback.
        
        Args:
            start_num: Starting chapter number
            count: Number of chapters to create
            
        Returns:
            List of Chapter objects
        """
        chapters = []
        for i in range(count):
            chapter_num = start_num + i
            chapters.append(Chapter(
                number=chapter_num,
                title=f"Chapter {chapter_num}",
                pov="To be determined",
                goal="Chapter goal to be determined",
                conflict="Conflict to be determined",
                word_count_target=8000,
                status="planned"
            ))
        return chapters
    
    def _create_default_plot_threads(self, num_chapters: int) -> List[PlotThread]:
        """
        Create default plot threads.
        
        Args:
            num_chapters: Total number of chapters
            
        Returns:
            List of PlotThread objects
        """
        all_chapters = list(range(1, num_chapters + 1))
        
        return [
            PlotThread(
                name="Main Plot",
                description="The primary storyline",
                status="active",
                chapters=all_chapters
            ),
            PlotThread(
                name="Character Development",
                description="Protagonist's growth and transformation",
                status="active",
                chapters=all_chapters
            )
        ]
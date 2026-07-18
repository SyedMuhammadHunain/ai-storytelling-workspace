"""Plot Architect Agent - Creates chapter-by-chapter outline."""

from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible
from ..models import Chapter, PlotThread


class PlotArchitectAgent(MockAgent):
    """
    Plot Architect Agent creates the story structure.
    
    Generates chapter-by-chapter outline with act breaks, POV,
    goals, conflicts, and pacing.
    """
    
    def __init__(self):
        """Initialize the Plot Architect Agent."""
        super().__init__(name="Plot Architect Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute plot architecture.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Create chapter outline
        chapters = self._create_mock_chapters()
        for chapter in chapters:
            bible.add_chapter(chapter)
            
        # Create plot threads
        plot_threads = self._create_mock_plot_threads()
        for thread in plot_threads:
            bible.add_plot_thread(thread)
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "chapters": len(chapters),
                "plot_threads": len(plot_threads)
            },
            summary=f"Created outline with {len(chapters)} chapters and {len(plot_threads)} plot threads"
        )
        
        self.log_action(f"Created {len(chapters)} chapter outline")
        self.log_end(success=True)
        
        return {
            "success": True,
            "chapters_count": len(chapters),
            "plot_threads_count": len(plot_threads)
        }
        
    def _create_mock_chapters(self) -> list:
        """Create mock chapter outline for MVP."""
        return [
            Chapter(
                number=1,
                title="The Awakening",
                pov="Aria Stormwind",
                goal="Introduce protagonist and inciting incident",
                conflict="Aria discovers her magic during a village crisis",
                word_count_target=8000,
                status="planned"
            ),
            Chapter(
                number=2,
                title="The Summons",
                pov="Aria Stormwind",
                goal="Aria is recruited by Master Eldrin",
                conflict="Aria must leave her home and face the unknown",
                word_count_target=8000,
                status="planned"
            ),
            Chapter(
                number=3,
                title="First Lessons",
                pov="Aria Stormwind",
                goal="Begin magical training",
                conflict="Aria struggles with self-doubt and control",
                word_count_target=8000,
                status="planned"
            ),
            Chapter(
                number=4,
                title="Shadows Rising",
                pov="Lord Malachar",
                goal="Introduce antagonist's perspective and plans",
                conflict="Malachar begins breaking the ancient seals",
                word_count_target=8000,
                status="planned"
            ),
            Chapter(
                number=5,
                title="The Ancient Forest",
                pov="Aria Stormwind",
                goal="Aria's first real test",
                conflict="Encounter with dark creatures in the forest",
                word_count_target=8000,
                status="planned"
            ),
            Chapter(
                number=6,
                title="Revelations",
                pov="Aria Stormwind",
                goal="Discover the true threat",
                conflict="Learn about Malachar and the weakening seals",
                word_count_target=8000,
                status="planned"
            ),
            Chapter(
                number=7,
                title="The Betrayal",
                pov="Aria Stormwind",
                goal="Major setback",
                conflict="Someone close betrays the group to Malachar",
                word_count_target=8000,
                status="planned"
            ),
            Chapter(
                number=8,
                title="Dark Fortress",
                pov="Aria Stormwind",
                goal="Infiltrate enemy stronghold",
                conflict="Rescue mission and confrontation with dark forces",
                word_count_target=8000,
                status="planned"
            ),
            Chapter(
                number=9,
                title="The Sacrifice",
                pov="Aria Stormwind",
                goal="Climactic battle preparation",
                conflict="Master Eldrin sacrifices himself to give Aria a chance",
                word_count_target=8000,
                status="planned"
            ),
            Chapter(
                number=10,
                title="Light Triumphant",
                pov="Aria Stormwind",
                goal="Final confrontation and resolution",
                conflict="Aria faces Malachar and must believe in herself to win",
                word_count_target=8000,
                status="planned"
            )
        ]
        
    def _create_mock_plot_threads(self) -> list:
        """Create mock plot threads for MVP."""
        return [
            PlotThread(
                name="Main Quest",
                description="Aria must stop Malachar from breaking the seals and unleashing dark magic",
                status="active",
                chapters=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            ),
            PlotThread(
                name="Aria's Training",
                description="Aria learns to control her magic and overcome self-doubt",
                status="active",
                chapters=[2, 3, 5, 6, 8, 9, 10]
            ),
            PlotThread(
                name="The Betrayal",
                description="A trusted ally is revealed to be working with Malachar",
                status="active",
                chapters=[4, 7, 8]
            ),
            PlotThread(
                name="Master Eldrin's Redemption",
                description="Eldrin seeks to atone for past failures",
                status="active",
                chapters=[2, 3, 6, 9]
            )
        ]

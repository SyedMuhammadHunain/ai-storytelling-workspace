"""Master Orchestrator - Coordinates all agents in the workflow."""

import logging
from typing import Optional
from pathlib import Path

from .story_bible import StoryBible
from .checkpoint import CheckpointManager, CheckpointDecision
from .agents.intake import IntakeAgent
from .agents.concept import ConceptAgent
from .agents.worldbuilding import WorldbuildingAgent
from .agents.character import CharacterAgent
from .agents.plot_architect import PlotArchitectAgent
from .agents.chapter_drafting import ChapterDraftingAgent
from .agents.continuity import ContinuityAgent
from .agents.dialogue_voice import DialogueVoiceAgent
from .agents.dev_editor import DevelopmentalEditorAgent
from .agents.line_editor import LineEditorAgent
from .agents.copy_editor import CopyEditorAgent
from .agents.proofreader import ProofreaderAgent
from .agents.front_matter import FrontMatterAgent
from .agents.back_matter import BackMatterAgent
from .agents.compilation import CompilationAgent
from .agents.qa import QAAgent
from .agents.export import ExportAgent


logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """
    Master orchestrator for the AI storytelling workflow.
    
    Coordinates all 15 agents, manages execution order, handles checkpoints,
    and provides progress logging.
    """
    
    def __init__(self, project_name: str, output_dir: str = "output"):
        """
        Initialize the orchestrator.
        
        Args:
            project_name: Name of the book project
            output_dir: Directory for output files
        """
        self.project_name = project_name
        self.output_dir = output_dir
        self.bible = StoryBible(project_name=project_name)
        
    def execute(self) -> bool:
        """
        Execute the complete workflow.
        
        Returns:
            True if workflow completed successfully, False if aborted
        """
        logger.info(f"Starting workflow for project: {self.project_name}")
        logger.info("=" * 70)
        
        try:
            # Phase 1: Setup
            if not self._phase_1_setup():
                return False
                
            # Phase 2: Architecture & Drafting
            if not self._phase_2_drafting():
                return False
                
            # Phase 3: Editing
            if not self._phase_3_editing():
                return False
                
            # Phase 4: Assembly & Export
            if not self._phase_4_assembly():
                return False
            
            logger.info("=" * 70)
            logger.info("✓ Workflow completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Workflow failed with error: {e}")
            return False
    
    def _phase_1_setup(self) -> bool:
        """Execute Phase 1: Setup agents."""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 1: SETUP")
        logger.info("=" * 70)
        
        # Agent 1: Intake
        logger.info("\n[1/15] Running Intake Agent...")
        intake = IntakeAgent()
        intake.execute(self.bible)
        
        # Checkpoint 1: Book Brief
        checkpoint = CheckpointManager.create_checkpoint_1()
        if checkpoint.execute(self.bible) == CheckpointDecision.ABORT:
            logger.info("Workflow aborted by user at Checkpoint 1")
            return False
        
        # Agent 2: Concept
        logger.info("\n[2/15] Running Concept Agent...")
        concept = ConceptAgent()
        concept.execute(self.bible)
        
        # Checkpoint 2: Concept
        checkpoint = CheckpointManager.create_checkpoint_2()
        if checkpoint.execute(self.bible) == CheckpointDecision.ABORT:
            logger.info("Workflow aborted by user at Checkpoint 2")
            return False
        
        # Agent 3: Worldbuilding
        logger.info("\n[3/15] Running Worldbuilding Agent...")
        worldbuilding = WorldbuildingAgent()
        worldbuilding.execute(self.bible)
        
        # Agent 4: Character
        logger.info("\n[4/15] Running Character Agent...")
        character = CharacterAgent()
        character.execute(self.bible)
        
        # Checkpoint 3: Story Bible v1
        checkpoint = CheckpointManager.create_checkpoint_3()
        if checkpoint.execute(self.bible) == CheckpointDecision.ABORT:
            logger.info("Workflow aborted by user at Checkpoint 3")
            return False
        
        return True
    
    def _phase_2_drafting(self) -> bool:
        """Execute Phase 2: Architecture & Drafting."""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 2: ARCHITECTURE & DRAFTING")
        logger.info("=" * 70)
        
        # Agent 5: Plot Architect
        logger.info("\n[5/15] Running Plot Architect Agent...")
        plot_architect = PlotArchitectAgent()
        plot_architect.execute(self.bible)
        
        # Checkpoint 4: Plot Outline (most important checkpoint)
        checkpoint = CheckpointManager.create_checkpoint_4()
        if checkpoint.execute(self.bible) == CheckpointDecision.ABORT:
            logger.info("Workflow aborted by user at Checkpoint 4")
            return False
        
        # Agent 6: Chapter Drafting (sequential batching for MVP)
        logger.info("\n[6/15] Running Chapter Drafting Agents...")
        logger.info("Drafting chapters sequentially (10 chapters)...")
        
        for chapter_num in range(1, 11):
            logger.info(f"  Drafting Chapter {chapter_num}/10...")
            chapter_agent = ChapterDraftingAgent(chapter_number=chapter_num)
            chapter_agent.execute(self.bible)
        
        # Agent 7: Continuity
        logger.info("\n[7/15] Running Continuity Agent...")
        continuity = ContinuityAgent()
        continuity.execute(self.bible)
        
        return True
    
    def _phase_3_editing(self) -> bool:
        """Execute Phase 3: Editing."""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 3: EDITING")
        logger.info("=" * 70)
        
        # Agent 8: Dialogue/Voice
        logger.info("\n[8/15] Running Dialogue/Voice Agent...")
        dialogue_voice = DialogueVoiceAgent()
        dialogue_voice.execute(self.bible)
        
        # Agent 9: Developmental Editor
        logger.info("\n[9/15] Running Developmental Editor Agent...")
        dev_editor = DevelopmentalEditorAgent()
        dev_editor.execute(self.bible)
        
        # Checkpoint 5: Developmental Notes
        checkpoint = CheckpointManager.create_checkpoint_5()
        if checkpoint.execute(self.bible) == CheckpointDecision.ABORT:
            logger.info("Workflow aborted by user at Checkpoint 5")
            return False
        
        # Agent 10: Line Editor
        logger.info("\n[10/15] Running Line Editor Agent...")
        line_editor = LineEditorAgent()
        line_editor.execute(self.bible)
        
        # Agent 11: Copy Editor
        logger.info("\n[11/15] Running Copy Editor Agent...")
        copy_editor = CopyEditorAgent()
        copy_editor.execute(self.bible)
        
        # Agent 12: Proofreader
        logger.info("\n[12/15] Running Proofreader Agent...")
        proofreader = ProofreaderAgent()
        proofreader.execute(self.bible)
        
        return True
    
    def _phase_4_assembly(self) -> bool:
        """Execute Phase 4: Assembly & Export."""
        logger.info("\n" + "=" * 70)
        logger.info("PHASE 4: ASSEMBLY & EXPORT")
        logger.info("=" * 70)
        
        # Agent 13: Front Matter
        logger.info("\n[13/15] Running Front Matter Agent...")
        front_matter = FrontMatterAgent()
        front_matter.execute(self.bible)
        
        # Agent 14: Back Matter
        logger.info("\n[14/15] Running Back Matter Agent...")
        back_matter = BackMatterAgent()
        back_matter.execute(self.bible)
        
        # Agent 15: Compilation
        logger.info("\n[15/15] Running Compilation Agent...")
        compilation = CompilationAgent()
        result = compilation.execute(self.bible)
        logger.info(f"  Compiled manuscript: {result['word_count']} words")
        
        # Agent 16: QA
        logger.info("\nRunning QA Agent...")
        qa = QAAgent()
        qa_result = qa.execute(self.bible)
        logger.info(f"  QA check: {qa_result['report']['status']}")
        if qa_result['issues']:
            logger.warning(f"  Found {len(qa_result['issues'])} issues")
        
        # Checkpoint 6: Final Sign-off
        checkpoint = CheckpointManager.create_checkpoint_6()
        if checkpoint.execute(self.bible) == CheckpointDecision.ABORT:
            logger.info("Workflow aborted by user at Checkpoint 6")
            return False
        
        # Agent 17: Export
        logger.info("\nRunning Export Agent...")
        export = ExportAgent(output_dir=self.output_dir)
        export_result = export.execute(self.bible)
        logger.info(f"  Exported to: {export_result['output_dir']}/")
        logger.info(f"    - {Path(export_result['manuscript_path']).name}")
        logger.info(f"    - {Path(export_result['story_bible_path']).name}")
        
        return True
    
    def get_story_bible(self) -> StoryBible:
        """Get the current Story Bible."""
        return self.bible

"""Human checkpoint system for workflow control."""

import sys
from typing import Optional, Literal
from enum import Enum

from .story_bible import StoryBible


class CheckpointDecision(Enum):
    """Possible decisions at a checkpoint."""
    APPROVE = "approve"
    EDIT = "edit"
    ABORT = "abort"


class Checkpoint:
    """
    Human checkpoint that pauses workflow execution.
    
    Displays current state, prompts user for decision, and returns
    the decision to the orchestrator for handling.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize a checkpoint.
        
        Args:
            name: Short name for this checkpoint
            description: Description of what's being reviewed
        """
        self.name = name
        self.description = description
        
    def execute(self, bible: StoryBible) -> CheckpointDecision:
        """
        Execute the checkpoint - pause and wait for user input.
        
        Args:
            bible: Current Story Bible state to display
            
        Returns:
            User's decision (approve/edit/abort)
        """
        self._display_checkpoint_header()
        self._display_story_bible_summary(bible)
        decision = self._prompt_user()
        return decision
        
    def _display_checkpoint_header(self) -> None:
        """Display checkpoint header."""
        print("\n" + "=" * 70)
        print(f"CHECKPOINT: {self.name}")
        print("=" * 70)
        print(f"\n{self.description}\n")
        
    def _display_story_bible_summary(self, bible: StoryBible) -> None:
        """Display current Story Bible state."""
        print("Current Story Bible State:")
        print("-" * 70)
        print(bible.get_summary())
        print("-" * 70)
        print()
        
    def _prompt_user(self) -> CheckpointDecision:
        """
        Prompt user for decision.
        
        Returns:
            User's decision
        """
        print("What would you like to do?")
        print("  1. Approve - Continue to next phase")
        print("  2. Edit - Make changes (not implemented in MVP)")
        print("  3. Abort - Stop execution")
        print()
        
        while True:
            try:
                choice = input("Enter your choice (1-3): ").strip()
                
                if choice == "1":
                    print("\n✓ Approved - Continuing...\n")
                    return CheckpointDecision.APPROVE
                elif choice == "2":
                    print("\n⚠ Edit mode not implemented in MVP")
                    print("Please approve to continue or abort to stop.\n")
                    continue
                elif choice == "3":
                    print("\n✗ Aborted - Stopping execution\n")
                    return CheckpointDecision.ABORT
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.\n")
                    
            except (EOFError, KeyboardInterrupt):
                print("\n\n✗ Interrupted - Stopping execution\n")
                return CheckpointDecision.ABORT


class CheckpointManager:
    """
    Manages checkpoints throughout the workflow.
    
    Provides predefined checkpoints for the standard workflow phases.
    """
    
    @staticmethod
    def create_checkpoint_1() -> Checkpoint:
        """Checkpoint 1: After intake, before concept development."""
        return Checkpoint(
            name="Checkpoint 1: Book Brief",
            description="Review the book brief before proceeding to concept development."
        )
        
    @staticmethod
    def create_checkpoint_2() -> Checkpoint:
        """Checkpoint 2: After concept, before world/character building."""
        return Checkpoint(
            name="Checkpoint 2: Concept",
            description="Review the concept before building the world and characters."
        )
        
    @staticmethod
    def create_checkpoint_3() -> Checkpoint:
        """Checkpoint 3: After world/character building, before plot architecture."""
        return Checkpoint(
            name="Checkpoint 3: Story Bible v1",
            description="Review the initial Story Bible (world, characters) before creating the plot outline."
        )
        
    @staticmethod
    def create_checkpoint_4() -> Checkpoint:
        """Checkpoint 4: After plot architecture, before drafting."""
        return Checkpoint(
            name="Checkpoint 4: Plot Outline",
            description="Review the chapter outline before starting the drafting phase. This is the most important checkpoint."
        )
        
    @staticmethod
    def create_checkpoint_5() -> Checkpoint:
        """Checkpoint 5: After developmental edit, before revision."""
        return Checkpoint(
            name="Checkpoint 5: Developmental Notes",
            description="Review developmental editor notes before making revisions."
        )
        
    @staticmethod
    def create_checkpoint_6() -> Checkpoint:
        """Checkpoint 6: Final sign-off before export."""
        return Checkpoint(
            name="Checkpoint 6: Final Sign-off",
            description="Final review before exporting the completed manuscript."
        )

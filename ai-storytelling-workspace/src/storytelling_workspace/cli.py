"""Command-line interface for AI Storytelling Workspace."""

import argparse
import logging
import sys
from pathlib import Path

from .orchestrator import WorkflowOrchestrator


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main() -> int:
    """
    Main CLI entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        prog='storytelling-workspace',
        description='AI-assisted book writing workflow orchestrator (MVP)',
        epilog='Example: python -m storytelling_workspace --project "My Fantasy Novel" --output ./my_book'
    )
    
    parser.add_argument(
        '--project',
        type=str,
        required=True,
        help='Name of the book project'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='Output directory for manuscript and Story Bible (default: output)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0 (MVP)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    # Print welcome banner
    print_banner()
    
    # Create and execute orchestrator
    try:
        orchestrator = WorkflowOrchestrator(
            project_name=args.project,
            output_dir=args.output
        )
        
        success = orchestrator.execute()
        
        if success:
            print_success_message(args.output)
            return 0
        else:
            print_abort_message()
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        return 1
    except Exception as e:
        logging.error(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def print_banner() -> None:
    """Print welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           AI Storytelling Workspace - MVP Orchestrator               ║
║                                                                      ║
║  Demonstrates 15-agent workflow for AI-assisted book writing         ║
║  with mock agents, Story Bible state management, and checkpoints     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")


def print_success_message(output_dir: str) -> None:
    """Print success message with output information."""
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                     ✓ WORKFLOW COMPLETED!                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

📁 Output files created in: {output_dir}/
   - manuscript.txt (compiled manuscript)
   - story_bible.json (complete Story Bible with all agent updates)

Next steps:
  1. Review the manuscript in {output_dir}/manuscript.txt
  2. Examine the Story Bible in {output_dir}/story_bible.json
  3. Check agent deltas to see how the story evolved

This MVP demonstrates the orchestration pattern. In production, replace
mock agents with real AI integrations for actual content generation.
""")


def print_abort_message() -> None:
    """Print abort message."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                     ⚠️  WORKFLOW ABORTED                             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

The workflow was stopped at a human checkpoint.
No output files were created.
""")


if __name__ == '__main__':
    sys.exit(main())

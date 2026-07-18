"""Tests for CLI interface."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

from storytelling_workspace.cli import main


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
@patch('sys.argv', ['cli.py', '--project', 'Test Book'])
def test_cli_main_with_defaults(mock_input):
    """Test CLI main function with default output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory so default 'output' dir is created there
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = main()
            
            # Should return 0 for success
            assert result == 0
            
            # Verify output files were created in default 'output' directory
            output_dir = os.path.join(tmpdir, "output")
            manuscript_path = os.path.join(output_dir, "manuscript.txt")
            story_bible_path = os.path.join(output_dir, "story_bible.json")
            
            assert os.path.exists(manuscript_path)
            assert os.path.exists(story_bible_path)
        finally:
            os.chdir(original_cwd)


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_cli_main_with_custom_output(mock_input):
    """Test CLI main function with custom output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('sys.argv', ['cli.py', '--project', 'Test Book', '--output', tmpdir]):
            result = main()
            
            # Should return 0 for success
            assert result == 0
            
            # Verify output files were created
            manuscript_path = os.path.join(tmpdir, "manuscript.txt")
            story_bible_path = os.path.join(tmpdir, "story_bible.json")
            
            assert os.path.exists(manuscript_path)
            assert os.path.exists(story_bible_path)


@patch('builtins.input', side_effect=KeyboardInterrupt())
def test_cli_main_handles_keyboard_interrupt(mock_input):
    """Test CLI main function handles Ctrl+C gracefully."""
    with patch('sys.argv', ['cli.py', '--project', 'Test Book']):
        result = main()
        
        # Should return 1 for interrupted execution
        assert result == 1


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
@patch('storytelling_workspace.orchestrator.WorkflowOrchestrator.execute', return_value=False)
def test_cli_main_handles_orchestrator_failure(mock_execute, mock_input):
    """Test CLI main function handles orchestrator failure."""
    with patch('sys.argv', ['cli.py', '--project', 'Test Book']):
        result = main()
        
        # Should return 1 for failed execution
        assert result == 1


@patch('builtins.input', side_effect=['1', '1', '1', '1', '1', '1'])
def test_cli_main_with_verbose_flag(mock_input):
    """Test CLI main function with verbose logging enabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('sys.argv', ['cli.py', '--project', 'Test Book', '--output', tmpdir, '--verbose']):
            result = main()
            
            # Should return 0 for success
            assert result == 0
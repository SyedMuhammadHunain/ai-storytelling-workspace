# AI Storytelling Workspace - Usage Guide

## Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/SyedMuhammadHunain/ai-storytelling-workspace.git
cd ai-storytelling-workspace
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install the package in development mode**:
```bash
pip install -e .
```

## Running the Application

### Method 1: Using the CLI Command

After installation, you can run the application directly:

```bash
python -m storytelling_workspace --project "My Fantasy Novel" --output ./my_book
```

### Method 2: Using Python Module

```bash
python -m storytelling_workspace --project "Epic Adventure" --output ./output
```

### Command-Line Options

```bash
python -m storytelling_workspace --help
```

**Available options**:
- `--project` (required): Name of your book project
- `--output` (optional): Output directory for manuscript and Story Bible (default: `output`)
- `--verbose` (optional): Enable verbose logging for debugging
- `--version`: Display version information

### Example Commands

**Basic usage with defaults**:
```bash
python -m storytelling_workspace --project "The Dragon's Quest"
```

**Custom output directory**:
```bash
python -m storytelling_workspace --project "Space Opera" --output ./my_books/space_opera
```

**Verbose logging**:
```bash
python -m storytelling_workspace --project "Mystery Novel" --verbose
```

## Workflow Execution

When you run the application, it will:

1. **Display welcome banner** with project information
2. **Execute 15 agents** in 4 phases:
   - Phase 1: Setup (Intake, Concept, Worldbuilding, Character)
   - Phase 2: Drafting (Plot Architect, Chapter Drafting, Continuity)
   - Phase 3: Editing (Dialogue/Voice, Dev Editor, Line Editor, Copy Editor, Proofreader)
   - Phase 4: Assembly (Front Matter, Back Matter, Compilation, QA, Export)
3. **Pause at 6 checkpoints** for human review:
   - Checkpoint 1: After book brief
   - Checkpoint 2: After concept development
   - Checkpoint 3: After world/character building
   - Checkpoint 4: After plot outline (most important)
   - Checkpoint 5: After developmental editing
   - Checkpoint 6: Final sign-off before export

### Checkpoint Interactions

At each checkpoint, you'll see:
```
======================================================================
CHECKPOINT: [Name]
======================================================================

[Description]

Current Story Bible State:
----------------------------------------------------------------------
[Summary of current state]
----------------------------------------------------------------------

What would you like to do?
  1. Approve - Continue to next phase
  2. Edit - Make changes (not implemented in MVP)
  3. Abort - Stop execution

Enter your choice (1-3):
```

**Options**:
- Press `1` to approve and continue
- Press `3` to abort the workflow
- Press `Ctrl+C` to interrupt at any time

## Output Files

After successful completion, you'll find two files in your output directory:

### 1. manuscript.txt
The complete compiled manuscript with:
- Front matter (title page, dedication, table of contents)
- All 10 chapters with full content
- Back matter (author bio, acknowledgments)

### 2. story_bible.json
Complete Story Bible containing:
- Book brief and concept
- Character profiles
- World rules and locations
- Timeline events
- Chapter outlines and content
- All agent deltas (change history)
- Metadata from all editing passes

## Testing the Application

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage

```bash
pytest tests/ --cov=storytelling_workspace --cov-report=term-missing
```

### Run Specific Test Files

```bash
# Test orchestrator
pytest tests/test_orchestrator.py -v

# Test agents
pytest tests/test_agents.py -v

# Test Story Bible
pytest tests/test_story_bible.py -v

# Test CLI
pytest tests/test_cli.py -v

# Test checkpoints
pytest tests/test_checkpoint.py -v
```

### Run Specific Test

```bash
pytest tests/test_orchestrator.py::test_orchestrator_execute_full_workflow -v
```

### Generate HTML Coverage Report

```bash
pytest tests/ --cov=storytelling_workspace --cov-report=html
# Open htmlcov/index.html in your browser
```

## Development Workflow

### Running in Development Mode

1. **Make changes to the code**
2. **Run tests to verify**:
```bash
pytest tests/ -v
```

3. **Check coverage**:
```bash
pytest tests/ --cov=storytelling_workspace --cov-report=term-missing
```

4. **Run end-to-end test**:
```bash
python -m storytelling_workspace --project "Test Book" --output ./test_output
```

### Code Quality Checks

**Run linter** (if configured):
```bash
flake8 src/storytelling_workspace
```

**Run type checker** (if configured):
```bash
mypy src/storytelling_workspace
```

## Troubleshooting

### Issue: Module not found

**Solution**: Make sure you've installed the package:
```bash
pip install -e .
```

### Issue: Permission denied when creating output directory

**Solution**: Ensure you have write permissions or use a different output directory:
```bash
python -m storytelling_workspace --project "My Book" --output ~/Documents/my_book
```

### Issue: Tests failing

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Virtual environment not activated

**Solution**: Activate the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Understanding the MVP

This is an **MVP (Minimum Viable Product)** that demonstrates:
- ✅ 15-agent workflow orchestration
- ✅ Story Bible state management
- ✅ Human checkpoint system
- ✅ Sequential agent execution
- ✅ Mock agent implementations

**What's NOT included in MVP**:
- ❌ Real AI integration (uses mock data)
- ❌ Edit mode at checkpoints (approve/abort only)
- ❌ Parallel agent execution
- ❌ Agent retry logic
- ❌ Incremental saves during workflow

## Next Steps

To evolve this MVP into production:

1. **Replace mock agents** with real AI integrations (OpenAI, Anthropic, etc.)
2. **Implement edit mode** at checkpoints for human intervention
3. **Add parallel execution** for independent agents
4. **Implement retry logic** for failed agent executions
5. **Add incremental saves** to prevent data loss
6. **Create web interface** for better user experience
7. **Add agent configuration** for customizing behavior
8. **Implement versioning** for Story Bible snapshots

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/SyedMuhammadHunain/ai-storytelling-workspace
- Issues: https://github.com/SyedMuhammadHunain/ai-storytelling-workspace/issues

## License

See LICENSE file for details.

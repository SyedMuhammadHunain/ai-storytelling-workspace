# AI Storytelling Workspace - MVP

A proof-of-concept orchestration system demonstrating a 15-agent workflow for AI-assisted book writing, featuring centralized state management via a "Story Bible" and human checkpoints at critical decision points.

## 🎯 Project Overview

This MVP demonstrates the **orchestration pattern** for coordinating multiple AI agents in a complex creative workflow. While the agents use mock implementations, the architecture showcases:

- **15 specialized agents** working sequentially through 4 phases
- **Story Bible**: Centralized state management with versioning and delta tracking
- **6 human checkpoints** for review and approval at critical junctures
- **Complete workflow**: From initial concept to final manuscript export

## 🏗️ Architecture

### Core Components

1. **Story Bible** (`story_bible.py`)
   - Central data structure storing all story elements
   - Version tracking with delta history
   - Serialization to/from JSON
   - Manages characters, locations, chapters, plot threads, timeline

2. **Base Agent** (`agents/base.py`)
   - Abstract base class for all agents
   - Automatic change recording and versioning
   - Logging integration
   - Mock agent implementation for MVP

3. **Checkpoint System** (`checkpoint.py`)
   - Human-in-the-loop decision points
   - Approve/Edit/Abort workflow control
   - Story Bible state display

4. **Orchestrator** (`orchestrator.py`)
   - Coordinates all 15 agents
   - Manages 4-phase execution
   - Integrates checkpoints
   - Progress logging

### The 15 Agents

#### Phase 1: Setup (Agents 1-4)
1. **Intake Agent** - Captures book parameters (genre, length, premise)
2. **Concept Agent** - Develops core concept and themes
3. **Worldbuilding Agent** - Creates locations and timeline
4. **Character Agent** - Develops protagonist, antagonist, supporting cast

#### Phase 2: Architecture & Drafting (Agents 5-7)
5. **Plot Architect Agent** - Creates 10-chapter outline with plot threads
6. **Chapter Drafting Agent** - Drafts all 10 chapters sequentially
7. **Continuity Agent** - Checks for plot holes and inconsistencies

#### Phase 3: Editing (Agents 8-12)
8. **Dialogue/Voice Agent** - Reviews character voice consistency
9. **Developmental Editor Agent** - Provides structural feedback
10. **Line Editor Agent** - Improves prose at sentence level
11. **Copy Editor Agent** - Fixes grammar, style, consistency
12. **Proofreader Agent** - Final typo and formatting check

#### Phase 4: Assembly (Agents 13-17)
13. **Front Matter Agent** - Generates title page, copyright, TOC
14. **Back Matter Agent** - Creates acknowledgments, author bio
15. **Compilation Agent** - Assembles complete manuscript
16. **QA Agent** - Validates completeness and quality
17. **Export Agent** - Outputs manuscript.txt and story_bible.json

### The 6 Checkpoints

1. **Book Brief** - After intake, before concept development
2. **Concept** - After concept, before worldbuilding
3. **Story Bible v1** - After world/characters, before plot outline
4. **Plot Outline** - After plot architecture, before drafting (most critical)
5. **Developmental Notes** - After dev editing, before line editing
6. **Final Sign-off** - Before export

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-storytelling-workspace

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## 📖 Usage

### Basic Usage

```bash
python -m storytelling_workspace --project "My Fantasy Novel"
```

### With Custom Output Directory

```bash
python -m storytelling_workspace --project "My Novel" --output ./my_book
```

### With Verbose Logging

```bash
python -m storytelling_workspace --project "My Novel" --verbose
```

### Command-Line Options

- `--project` (required): Name of your book project
- `--output` (optional): Output directory (default: `output`)
- `--verbose` (optional): Enable detailed logging
- `--version`: Show version information
- `--help`: Display help message

## 📁 Output Files

After successful execution, you'll find:

```
output/
├── manuscript.txt       # Complete compiled manuscript
└── story_bible.json    # Full Story Bible with all agent updates
```

### Manuscript Structure

The compiled manuscript includes:
- Front matter (title page, copyright, table of contents)
- All 10 chapters with content
- Back matter (acknowledgments, author bio)

### Story Bible Contents

The JSON file contains:
- Book brief and concept
- All characters with profiles
- Locations and world rules
- Timeline events
- Plot threads
- Chapter outlines and content
- All agent reports and edits
- Complete delta history
- Version information

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ -v --cov=storytelling_workspace --cov-report=term-missing
```

### Test Statistics

- **143 tests** covering all components
- **93% code coverage**
- All agents, Story Bible, checkpoints, and orchestrator tested

### Test Structure

```
tests/
├── test_story_bible.py          # Story Bible data structure
├── test_agents.py               # Base agent functionality
├── test_checkpoint.py           # Checkpoint system
├── test_orchestrator.py         # Workflow orchestration
└── test_agents/
    ├── test_intake.py
    ├── test_concept.py
    ├── test_worldbuilding.py
    ├── test_character.py
    ├── test_plot_architect.py
    ├── test_chapter_drafting.py
    ├── test_continuity.py
    ├── test_editing_agents.py
    └── test_assembly_agents.py
```

## 🔧 Development

### Project Structure

```
ai-storytelling-workspace/
├── src/storytelling_workspace/
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── cli.py                   # Command-line interface
│   ├── orchestrator.py          # Master orchestrator
│   ├── story_bible.py           # Central state management
│   ├── checkpoint.py            # Human checkpoint system
│   ├── models.py                # Data models
│   └── agents/
│       ├── base.py              # Base agent classes
│       ├── intake.py
│       ├── concept.py
│       ├── worldbuilding.py
│       ├── character.py
│       ├── plot_architect.py
│       ├── chapter_drafting.py
│       ├── continuity.py
│       ├── dialogue_voice.py
│       ├── dev_editor.py
│       ├── line_editor.py
│       ├── copy_editor.py
│       ├── proofreader.py
│       ├── front_matter.py
│       ├── back_matter.py
│       ├── compilation.py
│       ├── qa.py
│       └── export.py
├── tests/                       # Comprehensive test suite
├── tasks/                       # Project planning docs
├── setup.py                     # Package configuration
└── README.md                    # This file
```

### Adding a New Agent

1. Create agent file in `src/storytelling_workspace/agents/`
2. Inherit from `BaseAgent` or `MockAgent`
3. Implement `execute(bible: StoryBible) -> Dict[str, Any]`
4. Add to orchestrator workflow
5. Write tests in `tests/test_agents/`

Example:

```python
from .base import MockAgent
from ..story_bible import StoryBible

class MyAgent(MockAgent):
    def __init__(self):
        super().__init__(name="My Agent")
    
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        # Your logic here
        self._record_changes(bible, "My changes")
        return {"success": True}
```

## 🎓 Key Concepts

### Story Bible as Single Source of Truth

All agents read from and write to the Story Bible, ensuring:
- Consistent state across all agents
- Complete audit trail via deltas
- Easy serialization and persistence
- Version tracking for rollback capability

### Sequential Execution (MVP)

Agents run one at a time in a fixed order. This simplifies:
- Debugging and testing
- State management
- Checkpoint integration
- Progress tracking

**Production Note**: Real implementation would use parallel execution where possible (e.g., editing agents could run concurrently).

### Mock Agents

All agents in this MVP use mock implementations that:
- Generate placeholder content
- Demonstrate the orchestration pattern
- Enable testing without AI API dependencies
- Show expected input/output structure

**Production Note**: Replace mock agents with real AI integrations (OpenAI, Anthropic, etc.).

## 🚧 MVP Limitations

This is a **proof-of-concept** demonstrating orchestration patterns. Limitations include:

1. **Mock Content**: All agents generate placeholder text, not real AI content
2. **Sequential Only**: No parallel execution or batching optimizations
3. **Fixed Workflow**: No dynamic agent selection or conditional branching
4. **No Edit Capability**: Checkpoints can only approve or abort, not edit
5. **Simple Error Handling**: Basic error handling without retry logic
6. **No Persistence**: No database, only JSON file export
7. **Fixed Chapter Count**: Hardcoded to 10 chapters
8. **No Streaming**: Agents complete fully before returning

## 🔮 Production Roadmap

To evolve this MVP into a production system:

### Phase 1: Real AI Integration
- Replace mock agents with actual AI API calls
- Implement streaming for long-running operations
- Add token usage tracking and cost management
- Implement retry logic with exponential backoff

### Phase 2: Advanced Orchestration
- Parallel agent execution where possible
- Dynamic workflow based on story requirements
- Agent result validation and quality checks
- Conditional branching (e.g., skip editing if quality high)

### Phase 3: Enhanced Checkpoints
- Inline editing capabilities
- Diff visualization for changes
- Rollback to previous versions
- Collaborative review features

### Phase 4: Scalability
- Database persistence (PostgreSQL/MongoDB)
- Queue-based agent execution (Celery/RabbitMQ)
- Distributed processing
- Caching and optimization

### Phase 5: User Experience
- Web interface for workflow monitoring
- Real-time progress updates
- Agent output visualization
- Export to multiple formats (DOCX, EPUB, PDF)

## 📊 Performance

Current MVP performance (mock agents):
- **Full workflow**: ~0.1 seconds
- **Memory usage**: < 50MB
- **Output size**: ~7KB manuscript, ~38KB Story Bible

Production estimates (with real AI):
- **Full workflow**: 30-60 minutes (depending on API latency)
- **Token usage**: ~500K-1M tokens (varies by model and content)
- **Cost**: $5-20 per book (varies by provider and model)

## 🤝 Contributing

This is an MVP demonstration project. For production use:

1. Fork the repository
2. Replace mock agents with real implementations
3. Add error handling and retry logic
4. Implement proper logging and monitoring
5. Add integration tests with real AI APIs
6. Document your AI provider setup

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

This project demonstrates orchestration patterns for multi-agent AI systems, inspired by:
- LangChain's agent frameworks
- AutoGPT's autonomous agent architecture
- Traditional publishing workflows
- Software engineering best practices

## 📞 Support

For questions about the architecture or implementation:
- Review the code documentation
- Check the test suite for usage examples
- Examine the orchestrator flow in `orchestrator.py`

---

**Note**: This is an MVP demonstrating orchestration patterns. All content is generated by mock agents. For production use, integrate real AI models and implement proper error handling, monitoring, and scalability features.
# AI Storytelling Workspace

Multi-agent orchestration system for AI-assisted book writing, built on IBM Bob's architecture principles.

## Overview

This is an MVP implementation demonstrating a 15-agent workflow for collaborative book writing. The system uses mock agents with simple outputs to validate the orchestration pattern: proper agent sequencing, Story Bible state management, and human checkpoint handling.

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Quick Start

```bash
# Run the storytelling workspace
storytelling-workspace --project "My First Book"
```

## Project Structure

```
ai-storytelling-workspace/
├── src/
│   └── storytelling_workspace/
│       ├── agents/           # Agent implementations
│       ├── story_bible.py    # Story Bible data structures
│       ├── orchestrator.py   # Master orchestrator
│       └── cli.py           # CLI entry point
├── tests/
│   ├── test_agents/         # Agent tests
│   └── integration/         # Integration tests
├── tasks/
│   ├── plan.md             # Implementation plan
│   └── todo.md             # Task checklist
└── docs/
    └── examples/           # Example outputs
```

## Development Status

This is an MVP focused on demonstrating the orchestration pattern. Real AI integration is out of scope for this phase.

### Completed
- [x] Project structure setup
- [ ] Story Bible implementation
- [ ] Agent framework
- [ ] Orchestration system
- [ ] CLI interface

## Architecture

The system follows a master-orchestrator pattern with 15 specialized agents:

1. **Setup Phase**: Intake, Concept, Worldbuilding, Character
2. **Architecture Phase**: Plot Architect
3. **Drafting Phase**: Chapter Drafting, Continuity
4. **Editing Phase**: Dialogue/Voice, Developmental Editor, Line/Copy Editors, Proofreader
5. **Assembly Phase**: Front/Back Matter, Compilation, QA, Export

All agents coordinate through a shared Story Bible (JSON-based state).

## License

MIT

## Contributing

This is an MVP/proof-of-concept. Contributions welcome after initial implementation is complete.

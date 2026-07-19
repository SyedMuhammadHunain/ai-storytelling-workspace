# Development Guide

Welcome to the AI Storytelling Workspace development team! This document outlines our coding standards, workflows, and local setup.

## Local Environment Setup

We use `make` to simplify local development.

1. **Install Dependencies**:
   ```bash
   make setup
   ```
   *This installs Python dependencies via poetry/pip and Node modules for the Angular frontend.*

2. **Database Setup**:
   Ensure MySQL and Redis are running locally (or via `docker-compose up -d db redis`).
   ```bash
   make db-migrate
   ```

3. **Run Development Servers**:
   ```bash
   make dev
   ```
   *This starts FastAPI (port 8000), Angular (port 4200), and a local Celery worker.*

## Project Structure
```text
.
├── api/             # FastAPI backend (Routes, dependencies, websockets)
├── core/            # Core business logic (AI Providers, Caching, Config)
├── db/              # SQLAlchemy Models, Repositories, Migrations
├── agents/          # 18 AI Agent implementations
├── workers/         # Celery task definitions
├── web/             # Angular v22 Frontend
├── docs/            # Documentation
└── tests/           # Pytest suites
```

## Coding Standards

### Backend (Python)
- **Typing**: Strict type hinting is required.
- **Formatting**: We use `black` and `isort`.
- **Linting**: `flake8` and `mypy` must pass.
- **Async**: Use `async`/`await` for all I/O bound operations, including database calls (using AsyncSession) and AI Provider calls.

### Frontend (Angular)
- Follow the official Angular style guide.
- Use strict TypeScript mode.
- Use RxJS for state and asynchronous event streams.
- Use Angular Material components.

## Testing

We practice Test-Driven Development (TDD) for critical paths.

- **Run all tests**: `make test`
- **Run specific suite**: `pytest tests/unit/test_api/ -v`
- **Frontend tests**: `cd web && npm test`

*The CI pipeline requires 95%+ coverage for backend modules.*

## Git Workflow & PRs

1. Branch off `main` using the format: `feature/task-name`, `bugfix/issue-description`.
2. Write small, atomic commits.
3. Ensure all tests and linting pass locally before opening a Pull Request.
4. Update relevant documentation (e.g., `API_REFERENCE.md` if changing an endpoint).

## Adding a New Agent

1. Create the agent class in `agents/`. Inherit from `BaseAgent`.
2. Add the agent's prompt template to `utils/prompts.py`.
3. Create a corresponding Celery task in `workers/agent_tasks.py`.
4. Add unit tests in `tests/unit/test_agents/`.

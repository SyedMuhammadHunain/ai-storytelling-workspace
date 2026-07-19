# AI Storytelling Workspace v2.0

A comprehensive workspace for AI-assisted storytelling, novel generation, and story bible management. This platform orchestrates 18 specialized AI agents to help authors create, manage, and write complete stories with visual elements.

## Quick Start

1. Clone the repository
2. Configure your environment:
   ```bash
   cp .env.example .env
   # Add your Mistral/OpenAI API keys to .env
   ```
3. Use the Makefile to set up and run:
   ```bash
   make setup
   make dev
   ```

## Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install dependencies, set up environment |
| `make dev` | Start development servers (FastAPI, Celery, Angular) |
| `make test` | Run all tests (unit, integration) |
| `docker-compose up -d` | Start production Docker environment |
| `make db-migrate` | Run database migrations |

## Architecture Overview

The system follows a modern microservices-inspired architecture:

- **Frontend**: Angular v22, Angular Material, RxJS WebSocket integration
- **Backend**: FastAPI (Python 3.10+), SQLAlchemy (Async), Pydantic
- **Workers**: Celery with Redis broker for asynchronous AI tasks
- **Database**: MySQL 8.0 with Alembic for migrations
- **AI Integration**: Abstracted provider layer supporting Mistral (Text) and Pixtral (Images) with OpenAI fallback

For a deep dive, see [Architecture Documentation](docs/ARCHITECTURE.md).

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [AI Integration](docs/AI_INTEGRATION.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Database Migrations](docs/MIGRATIONS.md)

## Contributing

Please read the [Development Guide](docs/DEVELOPMENT.md) for coding standards, branching strategies, and our PR process. Ensure all code passes the `make test` checks before submitting.
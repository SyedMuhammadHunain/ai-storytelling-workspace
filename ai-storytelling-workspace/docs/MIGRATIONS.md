# Database Migrations Guide

## Overview

This project uses Alembic for database schema migrations with async SQLAlchemy support.

## Prerequisites

- Docker containers running (MySQL, phpMyAdmin, Redis)
- Virtual environment activated
- Environment variables configured in `.env`

## Quick Start

### 1. Start Docker Containers

```bash
docker-compose up -d
```

Wait for containers to be healthy:

```bash
docker-compose ps
```

### 2. Create Initial Migration

```bash
# Generate migration from models
alembic revision --autogenerate -m "Initial migration: Add all 8 database tables"
```

### 3. Apply Migration

```bash
# Run migration
alembic upgrade head
```

### 4. Verify Database

Access phpMyAdmin at http://localhost:8080:
- Server: `db`
- Username: `storytelling_user`
- Password: `storytelling_pass`
- Database: `storytelling_workspace`

## Common Commands

### Create New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Upgrade to specific revision
alembic upgrade <revision_id>
```

### Rollback Migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade to base (empty database)
alembic downgrade base
```

### View Migration History

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

## Migration Workflow

### 1. Modify Models

Edit files in `src/storytelling_workspace/db/models/`:

```python
# Example: Add new field to Project model
class Project(Base, UUIDMixin, TimestampMixin):
    # ... existing fields ...
    
    new_field: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="New field description"
    )
```

### 2. Generate Migration

```bash
alembic revision --autogenerate -m "Add new_field to Project"
```

### 3. Review Migration

Check the generated file in `alembic/versions/`:

```python
def upgrade() -> None:
    # Review auto-generated changes
    op.add_column('projects', sa.Column('new_field', ...))

def downgrade() -> None:
    # Review rollback logic
    op.drop_column('projects', 'new_field')
```

### 4. Apply Migration

```bash
alembic upgrade head
```

### 5. Test Rollback

```bash
# Test downgrade
alembic downgrade -1

# Re-apply
alembic upgrade head
```

## Configuration

### Database URL

Set in `.env`:

```bash
DATABASE_URL=mysql+aiomysql://storytelling_user:storytelling_pass@localhost:3306/storytelling_workspace
```

### Alembic Configuration

Edit `alembic.ini` for:
- File naming templates
- Logging levels
- Post-write hooks (black, ruff)

### Environment Configuration

Edit `alembic/env.py` for:
- Model imports
- Async engine configuration
- Migration context settings

## Troubleshooting

### Connection Refused

```
Error: Can't connect to MySQL server on 'localhost'
```

**Solution**: Start Docker containers:

```bash
docker-compose up -d
docker-compose ps  # Verify containers are running
```

### Migration Conflicts

```
Error: Target database is not up to date
```

**Solution**: Check current state and upgrade:

```bash
alembic current
alembic upgrade head
```

### Autogenerate Not Detecting Changes

**Solution**: Ensure models are imported in `alembic/env.py`:

```python
from storytelling_workspace.db.models import (
    Project, StoryBible, Chapter, ...
)
```

### Async Engine Issues

**Solution**: Verify `alembic/env.py` uses async engine:

```python
async def run_async_migrations() -> None:
    connectable = async_engine_from_config(...)
```

## Best Practices

1. **Always Review Generated Migrations**: Autogenerate is smart but not perfect
2. **Test Rollbacks**: Ensure `downgrade()` works before deploying
3. **Use Descriptive Messages**: `alembic revision -m "Clear description"`
4. **One Change Per Migration**: Keep migrations focused and atomic
5. **Version Control**: Commit migrations with code changes
6. **Backup Before Production**: Always backup production database before migrating

## Production Deployment

### 1. Backup Database

```bash
docker-compose exec db mysqldump -u storytelling_user -p storytelling_workspace > backup.sql
```

### 2. Apply Migrations

```bash
alembic upgrade head
```

### 3. Verify

```bash
alembic current
# Check application functionality
```

### 4. Rollback Plan

Keep backup and know the rollback command:

```bash
alembic downgrade <previous_revision>
```

## See Also

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Schema documentation

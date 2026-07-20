"""
Database session utilities for Celery workers.

Provides fresh engine/session per call to avoid 'Future attached to a different loop'
errors that occur when caching async engines across multiple Celery task executions.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from storytelling_workspace.config import settings

logger = logging.getLogger(__name__)


def _create_worker_engine() -> AsyncEngine:
    """Create a fresh async engine for worker use. Never cached."""
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        poolclass=NullPool,
    )


@asynccontextmanager
async def worker_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager that creates a FRESH engine + session every time.
    
    This avoids all loop-caching issues in Celery workers.
    The engine is disposed after the session closes.
    
    Usage:
        async with worker_session() as session:
            result = await session.execute(query)
            await session.commit()
    """
    engine = _create_worker_engine()
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    session = session_factory()
    
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"Worker session rollback: {e}")
        raise
    finally:
        await session.close()
        await engine.dispose()

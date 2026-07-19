"""
Database session management for async MySQL operations.

This module provides async session factory and dependency injection
for FastAPI endpoints and background workers.
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


# Global engine and session factory
_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_database_url() -> str:
    """
    Construct async MySQL database URL from settings.
    
    Returns:
        Database URL string for aiomysql driver
    """
    return (
        f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
        f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    )


def create_engine() -> AsyncEngine:
    """
    Create async SQLAlchemy engine with connection pooling.
    
    Returns:
        Configured AsyncEngine instance
    """
    database_url = get_database_url()
    
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Connection pool size
        max_overflow=20,  # Max connections beyond pool_size
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_timeout=30,  # Timeout for getting connection from pool
        # Use NullPool for testing to avoid connection issues
        poolclass=NullPool if settings.TESTING else None,
    )
    
    logger.info(f"Created async engine for {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
    return engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get or create async session factory.
    
    Returns:
        Configured async_sessionmaker instance
    """
    global _async_session_factory
    
    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autocommit=False,
            autoflush=False,
        )
        logger.info("Created async session factory")
    
    return _async_session_factory


def get_engine() -> AsyncEngine:
    """
    Get or create global async engine.
    
    Returns:
        Global AsyncEngine instance
    """
    global _engine
    
    if _engine is None:
        _engine = create_engine()
    
    return _engine


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    Usage:
        async with get_session() as session:
            result = await session.execute(query)
            await session.commit()
    
    Yields:
        AsyncSession instance
    """
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Session rollback due to error: {e}")
        raise
    finally:
        await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    
    Yields:
        AsyncSession instance
    """
    async with get_session() as session:
        yield session


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This should only be used in development/testing.
    In production, use Alembic migrations.
    """
    from storytelling_workspace.db.base import Base, import_models
    
    # Import all models to register them
    import_models()
    
    engine = get_engine()
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created")


async def drop_db() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    Only use in development/testing.
    """
    from storytelling_workspace.db.base import Base, import_models
    
    # Import all models to register them
    import_models()
    
    engine = get_engine()
    
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.warning("All database tables dropped")


async def close_db() -> None:
    """
    Close database engine and cleanup connections.
    
    Should be called on application shutdown.
    """
    global _engine, _async_session_factory
    
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("Database engine closed")
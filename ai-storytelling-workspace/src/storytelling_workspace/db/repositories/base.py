"""
Base repository with common CRUD operations.

Provides async database operations for all models.
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from storytelling_workspace.db.base import Base

logger = logging.getLogger(__name__)

# Type variable for model classes
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common CRUD operations.
    
    All repositories should inherit from this class and can override
    methods to add custom behavior.
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session
        self.logger = logging.getLogger(f"{__name__}.{model.__name__}Repository")
    
    async def create(self, **kwargs) -> ModelType:
        """
        Create a new record.
        
        Args:
            **kwargs: Model field values
            
        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        
        self.logger.info(f"Created {self.model.__name__} with id={instance.id}")
        return instance
    
    async def get_by_id(self, id: str | UUID) -> Optional[ModelType]:
        """
        Get record by ID.
        
        Args:
            id: Record ID (UUID string or UUID object)
            
        Returns:
            Model instance or None if not found
        """
        id_str = str(id) if isinstance(id, UUID) else id
        
        stmt = select(self.model).where(self.model.id == id_str)
        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()
        
        if instance:
            self.logger.debug(f"Found {self.model.__name__} with id={id_str}")
        else:
            self.logger.debug(f"{self.model.__name__} with id={id_str} not found")
        
        return instance
    
    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Get all records with optional pagination and ordering.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: Field name to order by (prefix with '-' for descending)
            
        Returns:
            List of model instances
        """
        stmt = select(self.model)
        
        # Apply ordering
        if order_by:
            if order_by.startswith('-'):
                # Descending order
                field = order_by[1:]
                stmt = stmt.order_by(getattr(self.model, field).desc())
            else:
                # Ascending order
                stmt = stmt.order_by(getattr(self.model, order_by))
        
        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        instances = result.scalars().all()
        
        self.logger.debug(f"Retrieved {len(instances)} {self.model.__name__} records")
        return list(instances)
    
    async def update(self, id: str | UUID, **kwargs) -> Optional[ModelType]:
        """
        Update record by ID.
        
        Args:
            id: Record ID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None if not found
        """
        id_str = str(id) if isinstance(id, UUID) else id
        
        # Get existing record
        instance = await self.get_by_id(id_str)
        if not instance:
            self.logger.warning(f"{self.model.__name__} with id={id_str} not found for update")
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        await self.session.flush()
        await self.session.refresh(instance)
        
        self.logger.info(f"Updated {self.model.__name__} with id={id_str}")
        return instance
    
    async def delete(self, id: str | UUID) -> bool:
        """
        Delete record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        id_str = str(id) if isinstance(id, UUID) else id
        
        # Check if exists
        instance = await self.get_by_id(id_str)
        if not instance:
            self.logger.warning(f"{self.model.__name__} with id={id_str} not found for deletion")
            return False
        
        # Delete
        await self.session.delete(instance)
        await self.session.flush()
        
        self.logger.info(f"Deleted {self.model.__name__} with id={id_str}")
        return True
    
    async def exists(self, id: str | UUID) -> bool:
        """
        Check if record exists.
        
        Args:
            id: Record ID
            
        Returns:
            True if exists, False otherwise
        """
        instance = await self.get_by_id(id)
        return instance is not None
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count total records with optional filters.
        
        Args:
            filters: Optional field name and value pairs for filtering
        
        Returns:
            Total number of records matching filters
        """
        stmt = select(self.model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(stmt)
        instances = result.scalars().all()
        count = len(instances)
        
        self.logger.debug(f"Counted {count} {self.model.__name__} records")
        return count
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        List records with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional field name and value pairs for filtering
            order_by: Field name to order by (prefix with '-' for descending)
            
        Returns:
            List of model instances
        """
        stmt = select(self.model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)
        
        # Apply ordering
        if order_by:
            if order_by.startswith('-'):
                # Descending order
                field = order_by[1:]
                stmt = stmt.order_by(getattr(self.model, field).desc())
            else:
                # Ascending order
                stmt = stmt.order_by(getattr(self.model, order_by))
        else:
            # Default ordering by updated_at desc if available
            if hasattr(self.model, 'updated_at'):
                stmt = stmt.order_by(self.model.updated_at.desc())
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        instances = result.scalars().all()
        
        self.logger.debug(f"Listed {len(instances)} {self.model.__name__} records")
        return list(instances)
    
    async def filter_by(self, **kwargs) -> List[ModelType]:
        """
        Filter records by field values.
        
        Args:
            **kwargs: Field name and value pairs
            
        Returns:
            List of matching model instances
        """
        stmt = select(self.model)
        
        # Apply filters
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(stmt)
        instances = result.scalars().all()
        
        self.logger.debug(
            f"Filtered {self.model.__name__} by {kwargs}, found {len(instances)} records"
        )
        return list(instances)
    
    async def get_or_create(self, defaults: Optional[Dict[str, Any]] = None, **kwargs) -> tuple[ModelType, bool]:
        """
        Get existing record or create new one.
        
        Args:
            defaults: Default values for creation if not found
            **kwargs: Filter criteria
            
        Returns:
            Tuple of (instance, created) where created is True if new record was created
        """
        # Try to find existing
        instances = await self.filter_by(**kwargs)
        
        if instances:
            self.logger.debug(f"Found existing {self.model.__name__}")
            return instances[0], False
        
        # Create new
        create_kwargs = {**kwargs}
        if defaults:
            create_kwargs.update(defaults)
        
        instance = await self.create(**create_kwargs)
        self.logger.info(f"Created new {self.model.__name__} with id={instance.id}")
        return instance, True

"""
Image repository for CRUD operations on Image model.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from storytelling_workspace.db.models.image import Image, ImageType
from storytelling_workspace.db.repositories.base import BaseRepository


class ImageRepository(BaseRepository[Image]):
    """Repository for Image model with custom queries."""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize Image repository.
        
        Args:
            session: Async database session
        """
        super().__init__(Image, session)
    
    async def get_by_project_id(self, project_id: str | UUID) -> List[Image]:
        """
        Get all images for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of images ordered by creation time (newest first)
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Image)
            .where(Image.project_id == project_id_str)
            .order_by(Image.created_at.desc())
        )
        
        result = await self.session.execute(stmt)
        images = result.scalars().all()
        
        self.logger.debug(f"Retrieved {len(images)} images for project {project_id_str}")
        return list(images)
    
    async def get_by_type(
        self,
        project_id: str | UUID,
        image_type: str
    ) -> List[Image]:
        """
        Get images by type for a project.
        
        Args:
            project_id: Project ID
            image_type: Type of image (cover_art, character_portrait, scene_illustration)
            
        Returns:
            List of images of the given type
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Image)
            .where(Image.project_id == project_id_str)
            .where(Image.image_type == image_type)
            .order_by(Image.created_at.desc())
        )
        
        result = await self.session.execute(stmt)
        images = result.scalars().all()
        
        self.logger.debug(
            f"Found {len(images)} {image_type} images for project {project_id_str}"
        )
        return list(images)
    
    async def get_cover_art(self, project_id: str | UUID) -> Optional[Image]:
        """
        Get cover art for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Cover art image or None if not found
        """
        images = await self.get_by_type(project_id, ImageType.COVER_ART.value)
        return images[0] if images else None
    
    async def get_character_portraits(self, project_id: str | UUID) -> List[Image]:
        """
        Get all character portraits for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of character portrait images
        """
        return await self.get_by_type(project_id, ImageType.CHARACTER_PORTRAIT.value)
    
    async def get_scene_illustrations(self, project_id: str | UUID) -> List[Image]:
        """
        Get all scene illustrations for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of scene illustration images
        """
        return await self.get_by_type(project_id, ImageType.SCENE_ILLUSTRATION.value)
    
    async def get_by_character(
        self,
        project_id: str | UUID,
        character_name: str
    ) -> Optional[Image]:
        """
        Get portrait for a specific character.
        
        Args:
            project_id: Project ID
            character_name: Character name
            
        Returns:
            Character portrait or None if not found
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Image)
            .where(Image.project_id == project_id_str)
            .where(Image.image_type == ImageType.CHARACTER_PORTRAIT.value)
            .where(Image.character_name == character_name)
            .order_by(Image.created_at.desc())
            .limit(1)
        )
        
        result = await self.session.execute(stmt)
        image = result.scalar_one_or_none()
        
        if image:
            self.logger.debug(f"Found portrait for character '{character_name}'")
        
        return image
    
    async def get_by_chapter(
        self,
        project_id: str | UUID,
        chapter_number: int
    ) -> Optional[Image]:
        """
        Get scene illustration for a specific chapter.
        
        Args:
            project_id: Project ID
            chapter_number: Chapter number
            
        Returns:
            Scene illustration or None if not found
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Image)
            .where(Image.project_id == project_id_str)
            .where(Image.image_type == ImageType.SCENE_ILLUSTRATION.value)
            .where(Image.chapter_number == chapter_number)
            .order_by(Image.created_at.desc())
            .limit(1)
        )
        
        result = await self.session.execute(stmt)
        image = result.scalar_one_or_none()
        
        if image:
            self.logger.debug(f"Found scene illustration for chapter {chapter_number}")
        
        return image
    
    async def get_total_cost(self, project_id: str | UUID) -> float:
        """
        Calculate total image generation cost for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Total cost in USD
        """
        images = await self.get_by_project_id(project_id)
        total_cost = sum(float(img.generation_cost) for img in images)
        
        self.logger.debug(f"Total image cost for project {project_id}: ${total_cost:.2f}")
        return total_cost
    
    async def get_by_provider(
        self,
        project_id: str | UUID,
        provider: str
    ) -> List[Image]:
        """
        Get images generated by a specific provider.
        
        Args:
            project_id: Project ID
            provider: Provider name (mistral, openai)
            
        Returns:
            List of images from the given provider
        """
        project_id_str = str(project_id) if isinstance(project_id, UUID) else project_id
        
        stmt = (
            select(Image)
            .where(Image.project_id == project_id_str)
            .where(Image.provider == provider)
            .order_by(Image.created_at.desc())
        )
        
        result = await self.session.execute(stmt)
        images = result.scalars().all()
        
        self.logger.debug(
            f"Found {len(images)} images from {provider} for project {project_id_str}"
        )
        return list(images)

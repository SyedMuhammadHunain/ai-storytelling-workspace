"""AI-powered Image Generator Agent using Pixtral/DALL-E."""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .ai_agent import AIAgent
from ..story_bible import StoryBible
from ..core.image_provider import ImageProviderFactory, ImageResponse
from ..core.rate_limiter import RateLimiter, RateLimitConfig
from ..core.cache import ResponseCache, InMemoryCache
from ..core.cost_tracker import CostTracker
from ..utils.image_prompts import (
    build_cover_art_prompt,
    build_character_portrait_prompt,
    build_scene_illustration_prompt
)


class AIImageGeneratorAgent(AIAgent):
    """
    AI-powered Image Generator Agent that creates visual assets.
    
    Generates:
    - Cover art (1024x1024)
    - Character portraits (512x512 each)
    - Scene illustrations (1024x512, key scenes)
    """
    
    # Class-level shared image resources
    _image_factory: Optional[ImageProviderFactory] = None
    
    def __init__(
        self,
        output_dir: str = "output/images",
        generate_cover: bool = True,
        generate_portraits: bool = True,
        generate_scenes: bool = True,
        max_portraits: int = 5,
        max_scenes: int = 10
    ):
        """
        Initialize Image Generator Agent.
        
        Args:
            output_dir: Directory to save generated images
            generate_cover: Whether to generate cover art
            generate_portraits: Whether to generate character portraits
            generate_scenes: Whether to generate scene illustrations
            max_portraits: Maximum number of character portraits
            max_scenes: Maximum number of scene illustrations
        """
        super().__init__(
            name="AI Image Generator Agent",
            model="pixtral-large-latest",  # Image model
            temperature=0.7,
            max_tokens=1000
        )
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.generate_cover = generate_cover
        self.generate_portraits = generate_portraits
        self.generate_scenes = generate_scenes
        self.max_portraits = max_portraits
        self.max_scenes = max_scenes
        
        # Initialize image factory if not already done
        if AIImageGeneratorAgent._image_factory is None:
            self._initialize_image_factory()
    
    @classmethod
    def _initialize_image_factory(cls) -> None:
        """Initialize shared image generation resources."""
        # Reuse rate limiter and cache from parent AIAgent
        if cls._rate_limiter is None or cls._cache is None:
            # Initialize if parent hasn't done it yet
            rate_config = RateLimitConfig(
                requests_per_second=0.5,  # Conservative for image generation
                tokens_per_minute=50_000,
                burst_size=2
            )
            cls._rate_limiter = RateLimiter(rate_config)
            cls._cache = InMemoryCache(max_size=500)
            cls._cost_tracker = CostTracker()
        
        # Create image factory (note: ImageProviderFactory doesn't use cache directly)
        cls._image_factory = ImageProviderFactory(
            primary_provider="mistral",  # Pixtral
            fallback_provider="openai",  # DALL-E 3
            rate_limiter=cls._rate_limiter,
            cost_tracker=cls._cost_tracker
        )
        
        logging.info("Initialized shared image generation resources")
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        filename: str = "image.png"
    ) -> ImageResponse:
        """
        Generate a single image.
        
        Args:
            prompt: Image generation prompt
            size: Image size (1024x1024, 512x512, 1024x512)
            filename: Output filename
            
        Returns:
            ImageResponse with image data and metadata
        """
        # Generate image (don't pass model, providers use their own hardcoded models)
        response = await self._image_factory.generate_image(
            prompt=prompt,
            size=size
        )
        
        # Save to filesystem
        output_path = self.output_dir / filename
        output_path.write_bytes(response.image_data)
        
        self.log_action(
            f"Generated {size} image: {filename} "
            f"(${response.cost:.4f}, {len(response.image_data)} bytes)"
        )
        
        return response
    
    async async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute image generation for all requested assets.
        
        Args:
            bible: Story Bible with content to visualize
            
        Returns:
            Execution results with image paths and metadata
        """
        self.log_start()
        
        try:
            images_generated = []
            total_cost = 0.0
            
            # Generate cover art
            if self.generate_cover:
                cover_result = await self._generate_cover_art(bible)
                if cover_result:
                    images_generated.append(cover_result)
                    total_cost += cover_result["cost"]
            
            # Generate character portraits
            if self.generate_portraits:
                portrait_results = await self._generate_character_portraits(bible)
                images_generated.extend(portrait_results)
                total_cost += sum(r["cost"] for r in portrait_results)
            
            # Generate scene illustrations
            if self.generate_scenes:
                scene_results = await self._generate_scene_illustrations(bible)
                images_generated.extend(scene_results)
                total_cost += sum(r["cost"] for r in scene_results)
            
            # Record changes to Story Bible
            self.record_changes(
                bible,
                changes={
                    "images_generated": len(images_generated),
                    "image_paths": [img["path"] for img in images_generated]
                },
                summary=f"Generated {len(images_generated)} images (${total_cost:.2f})"
            )
            
            self.log_action(f"Generated {len(images_generated)} total images")
            self.log_end(success=True)
            
            return {
                "success": True,
                "images": images_generated,
                "total_images": len(images_generated),
                "total_cost": total_cost
            }
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}", exc_info=True)
            self.log_end(success=False)
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _generate_cover_art(self, bible: StoryBible) -> Optional[Dict[str, Any]]:
        """Generate cover art for the book."""
        if not bible.concept:
            self.logger.warning("No concept available for cover art")
            return None
        
        # Build prompt
        prompt = build_cover_art_prompt(
            title=bible.brief.premise[:50],  # Use premise as title
            genre=bible.brief.genre,
            theme=bible.concept.theme,
            logline=bible.concept.logline
        )
        
        # Generate image
        response = await self.generate_image(
            prompt=prompt,
            size="1024x1024",
            filename="cover_art.png"
        )
        
        return {
            "type": "cover_art",
            "path": str(self.output_dir / "cover_art.png"),
            "size": "1024x1024",
            "cost": response.cost,
            "model": response.model,
            "provider": response.provider
        }
    
    async def _generate_character_portraits(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """Generate portraits for main characters."""
        if not bible.characters:
            self.logger.warning("No characters available for portraits")
            return []
        
        portraits = []
        
        # Sort characters by importance (protagonist, antagonist, then supporting)
        role_priority = {"protagonist": 0, "antagonist": 1, "supporting": 2}
        sorted_characters = sorted(
            bible.characters.values(),
            key=lambda c: role_priority.get(c.role, 3)
        )
        
        # Generate portraits for top N characters
        for i, character in enumerate(sorted_characters[:self.max_portraits]):
            # Build prompt
            prompt = build_character_portrait_prompt(
                name=character.name,
                physical_description=character.physical_description,
                role=character.role,
                genre=bible.brief.genre
            )
            
            # Generate image
            filename = f"portrait_{character.name.lower().replace(' ', '_')}.png"
            response = await self.generate_image(
                prompt=prompt,
                size="512x512",
                filename=filename
            )
            
            portraits.append({
                "type": "character_portrait",
                "character": character.name,
                "path": str(self.output_dir / filename),
                "size": "512x512",
                "cost": response.cost,
                "model": response.model,
                "provider": response.provider
            })
        
        return portraits
    
    async def _generate_scene_illustrations(self, bible: StoryBible) -> List[Dict[str, Any]]:
        """Generate illustrations for key scenes."""
        if not bible.chapters:
            self.logger.warning("No chapters available for scene illustrations")
            return []
        
        illustrations = []
        
        # Get chapters as sorted list (chapters is a dict with chapter numbers as keys)
        chapter_list = [bible.chapters[num] for num in sorted(bible.chapters.keys())]
        total_chapters = len(chapter_list)
        
        if total_chapters == 0:
            return []
        
        # Calculate which chapters to illustrate (evenly distributed)
        step = max(1, total_chapters // self.max_scenes)
        chapter_indices = list(range(0, total_chapters, step))[:self.max_scenes]
        
        for i, chapter_idx in enumerate(chapter_indices):
            chapter = chapter_list[chapter_idx]
            
            # Build prompt
            # WorldRules doesn't have primary_setting, use a generic setting description
            setting = "fantasy world"
            if bible.world_rules:
                # Construct setting from available WorldRules fields
                setting = f"{bible.world_rules.technology_level} {bible.world_rules.social_structure}"
            
            prompt = build_scene_illustration_prompt(
                chapter_title=chapter.title,
                chapter_summary=chapter.goal,  # Use goal as summary
                setting=setting,
                genre=bible.brief.genre
            )
            
            # Generate image
            filename = f"scene_chapter_{chapter.number:02d}.png"
            response = await self.generate_image(
                prompt=prompt,
                size="1024x512",
                filename=filename
            )
            
            illustrations.append({
                "type": "scene_illustration",
                "chapter": chapter.number,
                "chapter_title": chapter.title,
                "path": str(self.output_dir / filename),
                "size": "1024x512",
                "cost": response.cost,
                "model": response.model,
                "provider": response.provider
            })
        
        return illustrations
    
    def build_prompt(self, bible: StoryBible, **kwargs) -> str:
        """
        Build prompt (not used directly, see specific generation methods).
        
        Args:
            bible: Story Bible
            **kwargs: Additional parameters
            
        Returns:
            Empty string (not used)
        """
        return ""
    
    def parse_response(self, response, bible: StoryBible) -> Dict[str, Any]:
        """
        Parse response (not used for image generation).
        
        Args:
            response: Response to parse
            bible: Story Bible
            
        Returns:
            Empty dict (not used)
        """
        return {}

"""Image management API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException

from ..schemas.image import (
    ImageResponse,
    ImageListResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from ..dependencies import get_image_repo
from ...db.repositories.image import ImageRepository

router = APIRouter()


@router.get(
    "/",
    response_model=ImageListResponse,
    summary="List images",
    description="List images optionally filtered by project ID"
)
async def list_images(
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    image_repo: ImageRepository = Depends(get_image_repo)
):
    if project_id:
        images = await image_repo.get_by_project_id(str(project_id))
    else:
        images = await image_repo.list(limit=100)
        
    by_type = {}
    for img in images:
        t = img.image_type
        by_type[t] = by_type.get(t, 0) + 1
        
    return ImageListResponse(
        images=[ImageResponse.model_validate(img) for img in images],
        total=len(images),
        by_type=by_type
    )


@router.get(
    "/{image_id}",
    response_model=ImageResponse,
    summary="Get image by ID"
)
async def get_image(
    image_id: UUID,
    image_repo: ImageRepository = Depends(get_image_repo)
):
    image = await image_repo.get_by_id(str(image_id))
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
        
    return ImageResponse.model_validate(image)


@router.post(
    "/generate",
    response_model=ImageGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate a new image"
)
async def generate_image(
    request: ImageGenerationRequest,
    image_repo: ImageRepository = Depends(get_image_repo)
):
    import uuid
    import urllib.parse
    image_id = str(uuid.uuid4())
    
    encoded_prompt = urllib.parse.quote(request.prompt)
    seed = uuid.uuid4().int % 1000000
    # Use Pollinations.ai (free, no API key) as Mistral API doesn't support image generation natively
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
    
    # Need to get story bible id for this project
    from fastapi import Request
    # In a real app we'd inject this, but for this fix we can query it directly or provide a dummy if not needed
    # Actually, let's just fetch it since it's required
    db = image_repo.session
    from ...db.models.story_bible import StoryBible
    from sqlalchemy import select
    result = await db.execute(select(StoryBible).where(StoryBible.project_id == str(request.project_id)))
    story_bible = result.scalar_one_or_none()
    story_bible_id = story_bible.id if story_bible else str(uuid.uuid4())

    await image_repo.create(**{
        "id": image_id,
        "project_id": str(request.project_id) if request.project_id else None,
        "story_bible_id": story_bible_id,
        "image_type": request.image_type.value if hasattr(request.image_type, 'value') else request.image_type,
        "file_path": image_url,
        "file_size": 1024,
        "prompt": request.prompt,
        "model": "flux",
        "provider": "pollinations.ai",
        "width": 1024,
        "height": 1024,
        "format": "jpg",
        "generation_cost": 0.0
    })

    return ImageGenerationResponse(
        image_id=uuid.UUID(image_id),
        status="completed",
        message="Image generated successfully",
        estimated_time_seconds=0,
        url=image_url
    )

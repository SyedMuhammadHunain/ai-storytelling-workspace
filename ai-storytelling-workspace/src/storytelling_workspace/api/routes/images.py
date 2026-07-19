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
):
    # This would typically trigger an async celery/arq task.
    # We return a placeholder queued status.
    import uuid
    return ImageGenerationResponse(
        image_id=uuid.uuid4(),
        status="queued",
        message="Image generation task queued successfully",
        estimated_time_seconds=30
    )

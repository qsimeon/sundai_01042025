import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.database import execute_insert, execute_query
from api.dependencies import verify_api_key
from api.models import GenerateImageRequest, ImageResponse
from api.services.image_service import generate_image_async

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/generate",
    response_model=ImageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)]
)
async def generate_image(request: GenerateImageRequest) -> ImageResponse:
    """Generate an image using AI"""
    try:
        logger.info(f"Generating image with prompt: {request.prompt[:50]}...")

        # Use service to generate image
        image_data = await generate_image_async(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio
        )

        # Store in database
        image_id = execute_insert(
            """INSERT INTO images (prompt, file_path, model, aspect_ratio)
               VALUES (?, ?, ?, ?)""",
            (
                request.prompt,
                image_data["file_path"],
                image_data.get("model", "replicate-flux"),
                request.aspect_ratio
            )
        )

        # Retrieve and return
        images = execute_query("SELECT * FROM images WHERE id = ?", (image_id,))
        if images:
            return ImageResponse(**dict(images[0]))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created image"
        )

    except Exception as e:
        logger.error(f"Failed to generate image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=list[ImageResponse], dependencies=[Depends(verify_api_key)])
async def list_images(
    post_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> list[ImageResponse]:
    """List all images with optional filtering"""
    try:
        if post_id:
            images = execute_query(
                """SELECT * FROM images WHERE post_id = ?
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (post_id, limit, offset)
            )
        else:
            images = execute_query(
                """SELECT * FROM images
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (limit, offset)
            )

        return [ImageResponse(**dict(image)) for image in images]

    except Exception as e:
        logger.error(f"Failed to list images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{image_id}", response_model=ImageResponse, dependencies=[Depends(verify_api_key)])
async def get_image(image_id: int) -> ImageResponse:
    """Get a specific image by ID"""
    try:
        images = execute_query("SELECT * FROM images WHERE id = ?", (image_id,))

        if not images:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image {image_id} not found"
            )

        return ImageResponse(**dict(images[0]))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get image {image_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

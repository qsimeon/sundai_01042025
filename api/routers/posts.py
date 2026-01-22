import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.database import execute_insert, execute_query, execute_update
from api.dependencies import verify_api_key
from api.models import (
    ApprovePostRequest,
    GeneratePostRequest,
    PostResponse,
    PublishPostRequest,
)
from api.services.post_service import generate_post_async, publish_post_async

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/generate",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)]
)
async def generate_post(request: GeneratePostRequest) -> PostResponse:
    """Generate a new post using AI"""
    try:
        logger.info(f"Generating post of type: {request.post_type}")

        # Use service to generate post
        post_data = await generate_post_async(
            post_type=request.post_type.value,
            platform=request.platform,
            generate_image=request.generate_image
        )

        # Store in database
        post_id = execute_insert(
            """INSERT INTO posts
               (content, image_prompt, image_path, post_type, platform, status, character_count)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                post_data["content"],
                post_data.get("image_prompt"),
                post_data.get("image_path"),
                request.post_type.value,
                request.platform,
                "pending",
                len(post_data["content"])
            )
        )

        # Retrieve and return
        posts = execute_query("SELECT * FROM posts WHERE id = ?", (post_id,))
        if posts:
            return PostResponse(**dict(posts[0]))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created post"
        )

    except Exception as e:
        logger.error(f"Failed to generate post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=list[PostResponse], dependencies=[Depends(verify_api_key)])
async def list_posts(
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> list[PostResponse]:
    """List all posts with optional filtering"""
    try:
        if status:
            posts = execute_query(
                """SELECT * FROM posts WHERE status = ?
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (status, limit, offset)
            )
        else:
            posts = execute_query(
                """SELECT * FROM posts
                   ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (limit, offset)
            )

        return [PostResponse(**dict(post)) for post in posts]

    except Exception as e:
        logger.error(f"Failed to list posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{post_id}", response_model=PostResponse, dependencies=[Depends(verify_api_key)])
async def get_post(post_id: int) -> PostResponse:
    """Get a specific post by ID"""
    try:
        posts = execute_query("SELECT * FROM posts WHERE id = ?", (post_id,))

        if not posts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post {post_id} not found"
            )

        return PostResponse(**dict(posts[0]))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{post_id}/approve",
    response_model=PostResponse,
    dependencies=[Depends(verify_api_key)]
)
async def approve_post(post_id: int, request: ApprovePostRequest) -> PostResponse:
    """Approve or reject a post"""
    try:
        # Check post exists
        posts = execute_query("SELECT * FROM posts WHERE id = ?", (post_id,))
        if not posts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post {post_id} not found"
            )

        post = dict(posts[0])

        if request.approved:
            execute_update(
                "UPDATE posts SET status = ?, approved_at = CURRENT_TIMESTAMP WHERE id = ?",
                ("approved", post_id)
            )

            # Store approval in database
            execute_insert(
                """INSERT INTO approvals (content_type, content_id, approved)
                   VALUES (?, ?, ?)""",
                ("post", post_id, True)
            )

            logger.info(f"Post {post_id} approved")
        else:
            execute_update(
                "UPDATE posts SET status = ?, rejection_reason = ? WHERE id = ?",
                ("rejected", request.rejection_reason, post_id)
            )

            # Store rejection in database
            execute_insert(
                """INSERT INTO approvals (content_type, content_id, approved, rejection_reason)
                   VALUES (?, ?, ?, ?)""",
                ("post", post_id, False, request.rejection_reason)
            )

            # Store feedback for improvement
            execute_insert(
                """INSERT INTO rejection_feedback (content_type, content_preview, rejection_reason)
                   VALUES (?, ?, ?)""",
                ("post", post.get("content", "")[:200], request.rejection_reason)
            )

            logger.info(f"Post {post_id} rejected: {request.rejection_reason}")

        # Return updated post
        posts = execute_query("SELECT * FROM posts WHERE id = ?", (post_id,))
        return PostResponse(**dict(posts[0]))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{post_id}/publish",
    response_model=PostResponse,
    dependencies=[Depends(verify_api_key)]
)
async def publish_post(post_id: int, request: PublishPostRequest) -> PostResponse:
    """Publish an approved post"""
    try:
        # Check post exists and is approved
        posts = execute_query("SELECT * FROM posts WHERE id = ?", (post_id,))
        if not posts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post {post_id} not found"
            )

        post = dict(posts[0])

        if post["status"] != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Post must be approved before publishing (current status: {post['status']})"
            )

        if request.publish_to_mastodon:
            # Publish to Mastodon
            mastodon_response = await publish_post_async(post_id)

            # Update post with published info
            execute_update(
                """UPDATE posts SET status = ?, published_at = CURRENT_TIMESTAMP,
                   mastodon_url = ?, mastodon_id = ? WHERE id = ?""",
                ("published", mastodon_response.get("url"), mastodon_response.get("id"), post_id)
            )

            logger.info(f"Post {post_id} published to Mastodon: {mastodon_response.get('url')}")
        else:
            execute_update(
                "UPDATE posts SET status = ?, published_at = CURRENT_TIMESTAMP WHERE id = ?",
                ("published", post_id)
            )

        # Return updated post
        posts = execute_query("SELECT * FROM posts WHERE id = ?", (post_id,))
        return PostResponse(**dict(posts[0]))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

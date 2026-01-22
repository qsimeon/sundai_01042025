import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.database import execute_insert, execute_query, execute_update
from api.dependencies import verify_api_key
from api.models import (
    ApproveReplyRequest,
    GenerateReplyRequest,
    ReplyResponse,
    SearchRepliesRequest,
)
from api.services.reply_service import generate_reply_async, search_replies_async

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)]
)
async def search_replies(request: SearchRepliesRequest):
    """Search for posts to reply to"""
    try:
        logger.info(f"Searching for replies with hashtag: {request.hashtag}")

        # Use service to search
        opportunities = await search_replies_async(
            hashtag=request.hashtag,
            limit=request.limit
        )

        return {
            "hashtag": request.hashtag,
            "count": len(opportunities),
            "opportunities": opportunities
        }

    except Exception as e:
        logger.error(f"Failed to search replies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/generate",
    response_model=ReplyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)]
)
async def generate_reply(request: GenerateReplyRequest) -> ReplyResponse:
    """Generate a reply to a Mastodon post"""
    try:
        logger.info(f"Generating reply to post: {request.post_id}")

        # Use service to generate reply
        reply_data = await generate_reply_async(
            post_id=request.post_id,
            generate_image=request.generate_image
        )

        # Store in database
        reply_id = execute_insert(
            """INSERT INTO replies
               (post_id, reply_content, should_reply, reasoning, relevance_score, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                request.post_id,
                reply_data["content"],
                reply_data.get("should_reply", True),
                reply_data.get("reasoning"),
                reply_data.get("relevance_score"),
                "pending"
            )
        )

        # Retrieve and return
        replies = execute_query("SELECT * FROM replies WHERE id = ?", (reply_id,))
        if replies:
            return ReplyResponse(**dict(replies[0]))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created reply"
        )

    except Exception as e:
        logger.error(f"Failed to generate reply: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=list[ReplyResponse], dependencies=[Depends(verify_api_key)])
async def list_replies(
    status: Optional[str] = Query(None),
    post_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> list[ReplyResponse]:
    """List all replies with optional filtering"""
    try:
        query = "SELECT * FROM replies WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if post_id:
            query += " AND post_id = ?"
            params.append(post_id)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        replies = execute_query(query, tuple(params))
        return [ReplyResponse(**dict(reply)) for reply in replies]

    except Exception as e:
        logger.error(f"Failed to list replies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{reply_id}", response_model=ReplyResponse, dependencies=[Depends(verify_api_key)])
async def get_reply(reply_id: int) -> ReplyResponse:
    """Get a specific reply by ID"""
    try:
        replies = execute_query("SELECT * FROM replies WHERE id = ?", (reply_id,))

        if not replies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reply {reply_id} not found"
            )

        return ReplyResponse(**dict(replies[0]))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reply {reply_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{reply_id}/approve",
    response_model=ReplyResponse,
    dependencies=[Depends(verify_api_key)]
)
async def approve_reply(reply_id: int, request: ApproveReplyRequest) -> ReplyResponse:
    """Approve or reject a reply"""
    try:
        # Check reply exists
        replies = execute_query("SELECT * FROM replies WHERE id = ?", (reply_id,))
        if not replies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reply {reply_id} not found"
            )

        reply = dict(replies[0])

        if request.approved:
            execute_update(
                "UPDATE replies SET status = ?, approved_at = CURRENT_TIMESTAMP WHERE id = ?",
                ("approved", reply_id)
            )

            # Store approval
            execute_insert(
                """INSERT INTO approvals (content_type, content_id, approved)
                   VALUES (?, ?, ?)""",
                ("reply", reply_id, True)
            )

            logger.info(f"Reply {reply_id} approved")
        else:
            execute_update(
                "UPDATE replies SET status = ?, rejection_reason = ? WHERE id = ?",
                ("rejected", request.rejection_reason, reply_id)
            )

            # Store rejection
            execute_insert(
                """INSERT INTO approvals (content_type, content_id, approved, rejection_reason)
                   VALUES (?, ?, ?, ?)""",
                ("reply", reply_id, False, request.rejection_reason)
            )

            # Store feedback
            execute_insert(
                """INSERT INTO rejection_feedback (content_type, content_preview, rejection_reason)
                   VALUES (?, ?, ?)""",
                ("reply", reply.get("reply_content", "")[:200], request.rejection_reason)
            )

            logger.info(f"Reply {reply_id} rejected: {request.rejection_reason}")

        # Return updated reply
        replies = execute_query("SELECT * FROM replies WHERE id = ?", (reply_id,))
        return ReplyResponse(**dict(replies[0]))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve reply {reply_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

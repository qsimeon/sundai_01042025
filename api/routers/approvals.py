import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.database import execute_query
from api.dependencies import verify_api_key

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", dependencies=[Depends(verify_api_key)])
async def list_approvals(
    content_type: Optional[str] = Query(None),
    approved: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List all approvals with optional filtering"""
    try:
        query = "SELECT * FROM approvals WHERE 1=1"
        params = []

        if content_type:
            query += " AND content_type = ?"
            params.append(content_type)

        if approved is not None:
            query += " AND approved = ?"
            params.append(approved)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        approvals = execute_query(query, tuple(params))

        return {
            "total": len(approvals),
            "approvals": [dict(approval) for approval in approvals]
        }

    except Exception as e:
        logger.error(f"Failed to list approvals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats/summary", dependencies=[Depends(verify_api_key)])
async def approval_stats():
    """Get approval statistics"""
    try:
        # Get approval rates
        total_approvals = execute_query("SELECT COUNT(*) as count FROM approvals")[0]
        approved_count = execute_query("SELECT COUNT(*) as count FROM approvals WHERE approved = 1")[0]
        rejected_count = execute_query("SELECT COUNT(*) as count FROM approvals WHERE approved = 0")[0]

        total = total_approvals["count"]
        approved = approved_count["count"]
        rejected = rejected_count["count"]

        approval_rate = (approved / total * 100) if total > 0 else 0

        return {
            "total_approvals": total,
            "approved": approved,
            "rejected": rejected,
            "approval_rate": round(approval_rate, 2)
        }

    except Exception as e:
        logger.error(f"Failed to get approval stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from api.database import execute_query
from api.dependencies import verify_api_key
from api.models import AnalyticsEngagementResponse, AnalyticsPostResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/posts", response_model=AnalyticsPostResponse, dependencies=[Depends(verify_api_key)])
async def get_post_analytics() -> AnalyticsPostResponse:
    """Get post analytics and performance metrics"""
    try:
        total_posts = execute_query("SELECT COUNT(*) as count FROM posts")[0]["count"]
        published_posts = execute_query(
            "SELECT COUNT(*) as count FROM posts WHERE status = ?", ("published",)
        )[0]["count"]
        pending_posts = execute_query(
            "SELECT COUNT(*) as count FROM posts WHERE status = ?", ("pending",)
        )[0]["count"]
        rejected_posts = execute_query(
            "SELECT COUNT(*) as count FROM posts WHERE status = ?", ("rejected",)
        )[0]["count"]

        approval_rate = (
            (published_posts + reject_posts) / total_posts * 100
            if total_posts > 0
            else 0
        )

        # Placeholder for engagement - would be calculated from Mastodon API
        avg_engagement = 0.0

        return AnalyticsPostResponse(
            total_posts=total_posts,
            published_posts=published_posts,
            pending_posts=pending_posts,
            rejected_posts=rejected_posts,
            approval_rate=round(approval_rate, 2),
            avg_engagement=avg_engagement
        )

    except Exception as e:
        logger.error(f"Failed to get post analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/engagement", response_model=AnalyticsEngagementResponse, dependencies=[Depends(verify_api_key)])
async def get_engagement_analytics() -> AnalyticsEngagementResponse:
    """Get engagement analytics across all posts"""
    try:
        # Placeholder analytics - would be fetched from Mastodon API
        total_engagements = 0
        total_replies = 0
        total_likes = 0
        total_shares = 0

        published_posts = execute_query("SELECT COUNT(*) as count FROM posts WHERE status = ?", ("published",))
        published_count = published_posts[0]["count"] if published_posts else 0

        avg_engagement_per_post = (
            total_engagements / published_count if published_count > 0 else 0
        )

        return AnalyticsEngagementResponse(
            total_engagements=total_engagements,
            total_replies=total_replies,
            total_likes=total_likes,
            total_shares=total_shares,
            avg_engagement_per_post=avg_engagement_per_post,
            top_post_id=None,
            top_post_engagement=0
        )

    except Exception as e:
        logger.error(f"Failed to get engagement analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/api-usage", dependencies=[Depends(verify_api_key)])
async def get_api_usage():
    """Get API usage statistics"""
    try:
        usage_stats = execute_query(
            """SELECT endpoint, method, COUNT(*) as requests,
               AVG(response_time_ms) as avg_response_time,
               MAX(response_time_ms) as max_response_time
               FROM api_usage
               GROUP BY endpoint, method
               ORDER BY requests DESC"""
        )

        return {
            "total_requests": sum(s["requests"] for s in usage_stats),
            "endpoints": [dict(stat) for stat in usage_stats]
        }

    except Exception as e:
        logger.error(f"Failed to get API usage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

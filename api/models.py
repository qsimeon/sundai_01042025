from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PostType(str, Enum):
    """Types of posts that can be generated"""
    thought_leadership = "thought_leadership"
    company_update = "company_update"
    product_announcement = "product_announcement"
    industry_insight = "industry_insight"


class PostStatus(str, Enum):
    """Status of a post through its lifecycle"""
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    published = "published"


class ContentType(str, Enum):
    """Type of content (post or reply)"""
    post = "post"
    reply = "reply"


# Request Models
class GeneratePostRequest(BaseModel):
    """Request to generate a new post"""
    post_type: PostType = Field(..., description="Type of post to generate")
    platform: str = Field(default="mastodon", description="Target platform")
    generate_image: bool = Field(default=False, description="Whether to generate an image")


class ApprovePostRequest(BaseModel):
    """Request to approve or reject a post"""
    approved: bool = Field(..., description="Whether to approve or reject")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if rejected")


class PublishPostRequest(BaseModel):
    """Request to publish a post"""
    publish_to_mastodon: bool = Field(default=True, description="Whether to publish to Mastodon")


class SearchRepliesRequest(BaseModel):
    """Request to search for reply opportunities"""
    hashtag: str = Field(..., description="Hashtag to search for")
    limit: int = Field(default=10, description="Number of posts to search")


class GenerateReplyRequest(BaseModel):
    """Request to generate a reply"""
    post_id: str = Field(..., description="Mastodon post ID to reply to")
    generate_image: bool = Field(default=False, description="Whether to generate an image")


class ApproveReplyRequest(BaseModel):
    """Request to approve or reject a reply"""
    approved: bool = Field(..., description="Whether to approve or reject")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if rejected")


class GenerateImageRequest(BaseModel):
    """Request to generate an image"""
    prompt: str = Field(..., description="Image generation prompt")
    aspect_ratio: str = Field(default="1:1", description="Aspect ratio for the image")


# Response Models
class PostResponse(BaseModel):
    """Post response model"""
    id: int
    content: str
    image_prompt: Optional[str]
    image_path: Optional[str]
    post_type: str
    platform: str
    status: str
    character_count: Optional[int]
    created_at: str
    approved_at: Optional[str]
    published_at: Optional[str]
    mastodon_url: Optional[str]
    mastodon_id: Optional[str]
    rejection_reason: Optional[str]


class ReplyResponse(BaseModel):
    """Reply response model"""
    id: int
    post_id: str
    reply_content: str
    should_reply: Optional[bool]
    reasoning: Optional[str]
    relevance_score: Optional[int]
    status: str
    created_at: str
    approved_at: Optional[str]
    published_at: Optional[str]
    mastodon_url: Optional[str]
    rejection_reason: Optional[str]


class ImageResponse(BaseModel):
    """Image response model"""
    id: int
    prompt: str
    file_path: str
    model: Optional[str]
    aspect_ratio: Optional[str]
    created_at: str
    post_id: Optional[int]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    database: str = "connected"


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str]
    status_code: int


class AnalyticsPostResponse(BaseModel):
    """Post analytics response"""
    total_posts: int
    published_posts: int
    pending_posts: int
    rejected_posts: int
    approval_rate: float
    avg_engagement: float


class AnalyticsEngagementResponse(BaseModel):
    """Engagement analytics response"""
    total_engagements: int
    total_replies: int
    total_likes: int
    total_shares: int
    avg_engagement_per_post: float
    top_post_id: Optional[str]
    top_post_engagement: int

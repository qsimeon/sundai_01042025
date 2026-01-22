"""Service layer for reply generation"""

import asyncio
import logging
from typing import Any, Dict, List

from src.mastodon_client import MastodonClient
from src.post_generator import load_company_docs
from src.reply_generator import generate_replies

logger = logging.getLogger(__name__)


async def search_replies_async(
    hashtag: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for posts to reply to on Mastodon.

    Args:
        hashtag: Hashtag to search for
        limit: Maximum number of posts to retrieve

    Returns:
        List of post dictionaries from Mastodon
    """
    loop = asyncio.get_event_loop()

    try:
        # Create Mastodon client in executor
        mastodon = await loop.run_in_executor(None, MastodonClient)

        # Search for posts in executor
        posts = await loop.run_in_executor(
            None,
            mastodon.search_posts,
            hashtag,
            limit
        )

        logger.info(f"Found {len(posts)} posts for hashtag: {hashtag}")

        return [
            {
                "id": post.get("id"),
                "account": post.get("account", {}).get("acct", "unknown"),
                "content": post.get("content", "")[:200],
                "created_at": str(post.get("created_at", ""))
            }
            for post in posts
        ]

    except Exception as e:
        logger.error(f"Failed to search for replies: {e}")
        raise


async def generate_reply_async(
    post_id: str,
    generate_image_flag: bool = False
) -> Dict[str, Any]:
    """
    Generate a reply to a specific post.

    Args:
        post_id: Mastodon post ID to reply to
        generate_image_flag: Whether to generate an accompanying image

    Returns:
        Dictionary with reply data
    """
    loop = asyncio.get_event_loop()

    try:
        # Load company docs
        docs = await loop.run_in_executor(None, load_company_docs)

        # Create Mastodon client
        mastodon = await loop.run_in_executor(None, MastodonClient)

        # Fetch the post from Mastodon
        post = await loop.run_in_executor(
            None,
            mastodon.get_post,
            post_id
        )

        if not post:
            raise ValueError(f"Post {post_id} not found")

        # Generate replies for this single post
        replies = await loop.run_in_executor(
            None,
            generate_replies,
            docs,
            [post],
            5  # min_relevance
        )

        if not replies:
            return {
                "content": "",
                "should_reply": False,
                "reasoning": "No relevant reply generated",
                "relevance_score": 0
            }

        # Use the first reply
        reply = replies[0]

        result = {
            "content": reply.reply_content,
            "should_reply": reply.should_reply,
            "reasoning": reply.reasoning,
            "relevance_score": reply.relevance_score
        }

        return result

    except Exception as e:
        logger.error(f"Failed to generate reply for post {post_id}: {e}")
        raise

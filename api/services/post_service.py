"""Service layer for post generation and publishing"""

import asyncio
import logging
from typing import Any, Dict

from src.image_generator import generate_image
from src.mastodon_client import MastodonClient
from src.post_generator import format_post_for_platform, generate_post, load_company_docs

logger = logging.getLogger(__name__)


async def generate_post_async(
    post_type: str,
    platform: str,
    generate_image_flag: bool = False
) -> Dict[str, Any]:
    """
    Generate a post asynchronously using existing post generator.

    Args:
        post_type: Type of post (thought_leadership, customer_story, etc.)
        platform: Target platform (linkedin, twitter, mastodon)
        generate_image_flag: Whether to generate an accompanying image

    Returns:
        Dictionary with post data including content, image_prompt, and image_path
    """
    loop = asyncio.get_event_loop()

    try:
        # Load company docs in executor
        docs = await loop.run_in_executor(None, load_company_docs)

        # Generate post in executor
        post = await loop.run_in_executor(
            None,
            generate_post,
            docs,
            post_type,
            platform
        )

        # Format post for platform
        formatted_content = format_post_for_platform(post)

        result = {
            "content": formatted_content,
            "image_prompt": post.image_prompt,
            "post_type": post.post_type,
            "platform": post.platform
        }

        # Generate image if requested
        if generate_image_flag:
            try:
                image_path = await loop.run_in_executor(
                    None,
                    generate_image,
                    post.image_prompt
                )
                result["image_path"] = image_path
            except Exception as e:
                logger.warning(f"Failed to generate image: {e}")
                result["image_path"] = None

        return result

    except Exception as e:
        logger.error(f"Failed to generate post: {e}")
        raise


async def publish_post_async(
    post_id: int,
    content: str,
    image_path: str = None
) -> Dict[str, Any]:
    """
    Publish a post to Mastodon.

    Args:
        post_id: Database ID of the post
        content: Post content to publish
        image_path: Optional path to image file

    Returns:
        Dictionary with published post data (url, id, etc.)
    """
    loop = asyncio.get_event_loop()

    try:
        # Create Mastodon client in executor
        mastodon = await loop.run_in_executor(None, MastodonClient)

        # Publish post in executor
        status = await loop.run_in_executor(
            None,
            mastodon.post,
            content,
            image_path
        )

        logger.info(f"Post {post_id} published to Mastodon: {status.get('url')}")

        return {
            "url": status.get("url"),
            "id": status.get("id"),
            "created_at": status.get("created_at")
        }

    except Exception as e:
        logger.error(f"Failed to publish post {post_id}: {e}")
        raise

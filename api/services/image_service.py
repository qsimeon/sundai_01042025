"""Service layer for image generation"""

import asyncio
import logging
from typing import Any, Dict

from src.image_generator import generate_image

logger = logging.getLogger(__name__)


async def generate_image_async(
    prompt: str,
    aspect_ratio: str = "1:1"
) -> Dict[str, Any]:
    """
    Generate an image asynchronously using Replicate API.

    Args:
        prompt: Text description for image generation
        aspect_ratio: Image aspect ratio (1:1, 16:9, 3:2, 4:5, etc.)

    Returns:
        Dictionary with image data including file_path and model
    """
    loop = asyncio.get_event_loop()

    try:
        # Generate image in executor
        file_path = await loop.run_in_executor(
            None,
            generate_image,
            prompt,
            "generated_images",  # output_dir
            None,  # model (uses env var)
            None,  # trigger_word (uses env var)
            aspect_ratio
        )

        logger.info(f"Image generated successfully: {file_path}")

        return {
            "file_path": file_path,
            "model": "replicate-flux",
            "aspect_ratio": aspect_ratio
        }

    except Exception as e:
        logger.error(f"Failed to generate image: {e}")
        raise

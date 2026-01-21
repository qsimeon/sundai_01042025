"""
Image Generator using Replicate API
Generates images using custom Flux LoRA model
"""

import os
import replicate
import requests
from pathlib import Path
from typing import Optional


def generate_image(
    prompt: str,
    output_dir: str = "generated_images",
    model: Optional[str] = None,
    trigger_word: Optional[str] = None,
    aspect_ratio: str = "1:1",
    num_inference_steps: int = 28,
    guidance_scale: float = 3.0,
) -> str:
    """
    Generate an image using Replicate API with custom Flux LoRA model.

    Args:
        prompt: Text description for image generation
        output_dir: Directory to save generated images
        model: Replicate model ID (defaults to env var REPLICATE_MODEL)
        trigger_word: Trigger word to activate trained concept (defaults to env var)
        aspect_ratio: Image aspect ratio (1:1, 16:9, 3:2, 4:5, etc.)
        num_inference_steps: Number of denoising steps (1-50)
        guidance_scale: How closely to follow prompt (0-10)

    Returns:
        Path to downloaded image file
    """
    # Get configuration from environment
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        raise ValueError("REPLICATE_API_TOKEN not found in environment variables")

    model = model or os.getenv("REPLICATE_MODEL")
    if not model:
        raise ValueError("REPLICATE_MODEL not found in environment variables")

    trigger_word = trigger_word or os.getenv("REPLICATE_TRIGGER_WORD", "")

    # Add trigger word to prompt if provided
    if trigger_word:
        full_prompt = f"{trigger_word} {prompt}"
    else:
        full_prompt = prompt

    print(f"🎨 Generating image...")
    print(f"   Model: {model.split(':')[0]}")
    print(f"   Prompt: {full_prompt}")

    # Run the model
    output = replicate.run(
        model,
        input={
            "prompt": full_prompt,
            "aspect_ratio": aspect_ratio,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "output_format": "png",
            "output_quality": 90,
        }
    )

    # output is a list of FileOutput objects
    if not output:
        raise ValueError("No image generated")

    # Get the first image URL
    image_url = output[0]  # FileOutput object that acts like a URL
    print(f"   ✓ Image generated: {image_url}")

    # Download the image
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Create filename from prompt (sanitized)
    filename = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in prompt)
    filename = filename[:50]  # Limit length
    filepath = output_path / f"{filename}.png"

    # Download
    print(f"   📥 Downloading to {filepath}...")
    response = requests.get(str(image_url))
    response.raise_for_status()

    with open(filepath, 'wb') as f:
        f.write(response.content)

    print(f"   ✅ Saved: {filepath}")
    return str(filepath)


def generate_image_prompt(post_content: str, company_context: str) -> str:
    """
    Generate a concise image prompt based on post content.

    For the custom Pikachu model, this creates prompts that work well
    with the trained LoRA while matching the post theme.

    Args:
        post_content: The social media post text
        company_context: Company information for context

    Returns:
        Image generation prompt
    """
    # Extract key themes from post
    # For InventoryVision AI (retail + computer vision), create relevant scenes

    keywords = {
        "retail": "in a modern retail store with shelves",
        "inventory": "looking at shelves with products",
        "technology": "with futuristic tech elements",
        "ai": "with holographic displays",
        "automation": "in an automated warehouse",
        "camera": "looking at a security camera",
        "vision": "analyzing products with glowing eyes",
        "efficiency": "organizing products efficiently",
        "data": "surrounded by floating data visualizations",
    }

    # Find relevant keywords in post
    post_lower = post_content.lower()
    scene_elements = []

    for keyword, scene in keywords.items():
        if keyword in post_lower:
            scene_elements.append(scene)

    # Build prompt
    if scene_elements:
        scene = scene_elements[0]  # Use first match
    else:
        scene = "in a modern tech environment"

    # Create a prompt that works well with the Pikachu LoRA
    # The trigger word (SFHO932) will be added automatically
    prompt = f"character {scene}, professional lighting, detailed, high quality"

    return prompt


if __name__ == "__main__":
    # Test image generation
    from dotenv import load_dotenv
    load_dotenv(override=True)

    # Test prompt
    test_prompt = "character in a retail store analyzing shelves, professional lighting, detailed"

    print("="*60)
    print("IMAGE GENERATOR TEST")
    print("="*60)

    try:
        filepath = generate_image(
            prompt=test_prompt,
            aspect_ratio="1:1",
            num_inference_steps=28,
        )

        print(f"\n✅ Success! Image saved to: {filepath}")
        print(f"\nTo view: open {filepath}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

"""
Social Media Post Generator (OpenAI Version)
Uses OpenAI's GPT with structured outputs to generate brand-aligned social media posts
"""

from openai import OpenAI
from pydantic import BaseModel, Field
import os
from pathlib import Path
from typing import Literal


class SocialMediaPost(BaseModel):
    """Structured output schema for social media posts"""
    content: str = Field(description="The main post content. CRITICAL: For Mastodon, must be MAXIMUM 350 characters (500 char limit total with hashtags).")
    hashtags: list[str] = Field(description="3-4 relevant hashtags without the # symbol. Keep tags short.")
    platform: Literal["linkedin", "twitter", "mastodon"] = Field(description="Target platform for this post")
    post_type: str = Field(description="Type of post: thought_leadership, customer_story, product_update, industry_insight, etc.")
    call_to_action: str | None = Field(description="Optional call-to-action. For Mastodon, skip this to save characters.")


def load_company_docs(docs_dir: str = "company_docs", use_notion: bool = True) -> dict[str, str]:
    """
    Load all company documentation files from Notion or local directory

    Args:
        docs_dir: Path to directory containing company documentation markdown files (fallback)
        use_notion: If True, load from Notion API. If False, load from local files.

    Returns:
        Dictionary mapping document names to their content
    """
    if use_notion:
        # Try to load from Notion first
        try:
            from notion_loader import load_company_docs_from_notion
            print("Loading company docs from Notion...")
            return load_company_docs_from_notion()
        except Exception as e:
            print(f"Warning: Could not load from Notion: {e}")
            print("Falling back to local files...")
            use_notion = False

    # Load from local files
    docs_path = Path(docs_dir)
    docs = {}

    if not docs_path.exists():
        raise FileNotFoundError(f"Company docs directory not found: {docs_dir}")

    for doc_file in docs_path.glob("*.md"):
        with open(doc_file, 'r', encoding='utf-8') as f:
            docs[doc_file.stem] = f.read()

    if not docs:
        raise ValueError(f"No markdown files found in {docs_dir}")

    print(f"Loaded {len(docs)} company documents from local files")
    return docs


def create_llm_client() -> OpenAI:
    """
    Create LLM client (supports both direct OpenAI and OpenRouter)

    Set USE_OPENROUTER=true in .env to use OpenRouter instead of OpenAI.
    OpenRouter gives you access to multiple AI models through one API.
    """
    use_openrouter = os.getenv('USE_OPENROUTER', 'false').lower() == 'true'

    if use_openrouter:
        # Use OpenRouter - access to multiple AI models
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        print("Using OpenRouter API...")
        return OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    else:
        # Use OpenAI directly
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        return OpenAI(api_key=api_key)


def generate_post(
    company_docs: dict[str, str],
    post_type: str = "thought_leadership",
    platform: str = "mastodon",
    model: str = "openai/gpt-4o-mini" 
) -> SocialMediaPost:
    """
    Generate a social media post using LLMs with structured outputs

    Args:
        company_docs: Dictionary of company documentation
        post_type: Type of post to generate (thought_leadership, customer_story, etc.)
        platform: Target platform (linkedin, twitter, mastodon)
        model: OpenRouter model to use (openai/gpt-4o-mini is cheap and good)

    Returns:
        SocialMediaPost object with structured content
    """
    client = create_llm_client()

    # Combine all company docs into context
    context = "\n\n".join([
        f"# Document: {name}\n{content}"
        for name, content in company_docs.items()
    ])

    # Truncate context if too long (keep first 15000 chars)
    if len(context) > 15000:
        context = context[:15000] + "\n\n[... additional context truncated ...]"

    system_prompt = """You are a social media expert creating posts for InventoryVision AI,
a cutting-edge retail technology company. Your posts should:

- Be engaging and provide genuine value to retail professionals
- Demonstrate expertise without being overly salesy
- Use a confident but humble tone (technical but accessible)
- Include concrete examples or data points when possible
- Be authentic and align with the brand voice
- End with a subtle call-to-action when appropriate

Focus on educating, inspiring, and building community rather than just promoting."""

    platform_guidelines = {
        "linkedin": "Professional tone, 150-250 words, focus on business value and ROI",
        "twitter": "Concise and punchy, under 280 characters, engaging hook",
        "mastodon": "Authentic and community-focused. CRITICAL: Content MAXIMUM 350 characters. Skip call_to_action field. Use 3-4 SHORT hashtags only."
    }

    user_prompt = f"""Based on this company documentation:

{context}

Create a {post_type} social media post for {platform.title()} that:
- Follows the {platform} style: {platform_guidelines.get(platform, 'Authentic and engaging')}
- Is engaging and valuable to retail professionals and technology enthusiasts
- Includes 3-5 relevant hashtags
- Follows our brand voice (confident but humble, technical but accessible)
- Provides actionable insights or thought-provoking ideas

{"CRITICAL MASTODON LIMITS:\n- Content field: MAXIMUM 350 characters\n- Hashtags: Use 3-4 SHORT tags (not 5)\n- call_to_action: MUST be null/empty\n- Total post with hashtags must be under 500 characters\nBe extremely concise. Every character counts!" if platform == "mastodon" else ""}

Post type focus:
- thought_leadership: Share insights about retail technology trends
- customer_story: Highlight potential customer benefits (use hypothetical examples)
- product_update: Explain a specific feature or capability
- industry_insight: Comment on retail industry trends or news"""

    print(f"Generating {post_type} post for {platform} using {model}...")

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=SocialMediaPost,
    )

    post = response.choices[0].message.parsed
    print(f"✓ Generated post ({len(post.content)} characters)")

    return post


def format_post_for_platform(post: SocialMediaPost) -> str:
    """
    Format a SocialMediaPost for posting to a platform

    Args:
        post: SocialMediaPost object

    Returns:
        Formatted string ready to post
    """
    hashtags = " ".join([f"#{tag}" for tag in post.hashtags])

    if post.call_to_action:
        return f"{post.content}\n\n{post.call_to_action}\n\n{hashtags}"
    else:
        return f"{post.content}\n\n{hashtags}"


if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    load_dotenv(override=True)

    # Load company docs
    docs = load_company_docs()

    # Generate a thought leadership post
    post = generate_post(docs, post_type="thought_leadership", platform="mastodon")

    print("\n" + "="*60)
    print("GENERATED POST")
    print("="*60)
    print(f"\nType: {post.post_type}")
    print(f"Platform: {post.platform}")
    print(f"\n{format_post_for_platform(post)}")
    print("\n" + "="*60)

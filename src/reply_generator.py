"""
Automated Reply Generator (OpenAI Version)
Uses OpenAI's GPT with structured outputs to generate thoughtful replies to relevant posts
"""

from openai import OpenAI
from pydantic import BaseModel, Field
import os
from typing import List, Dict, Any
import re


class Reply(BaseModel):
    """Schema for a single reply"""
    post_id: str = Field(description="ID of the post to reply to")
    reply_content: str = Field(description="The reply text content (brief, 1-3 sentences)")
    should_reply: bool = Field(description="Whether this post warrants a reply")
    reasoning: str = Field(description="Why we should or shouldn't reply to this post")
    relevance_score: int = Field(description="How relevant this post is to our company (1-10)")


class BatchReplies(BaseModel):
    """Schema for batch reply generation"""
    replies: List[Reply] = Field(description="List of potential replies to posts")


def create_llm_client() -> OpenAI:
    """
    Create OpenAI client (supports both direct OpenAI and OpenRouter)

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


def clean_html(html_content: str) -> str:
    """
    Remove HTML tags from content

    Args:
        html_content: HTML string

    Returns:
        Plain text string
    """
    # Replace common HTML elements
    text = html_content.replace('<p>', '').replace('</p>', '\n')
    text = text.replace('<br />', '\n').replace('<br>', '\n')

    # Remove all HTML tags
    text = re.sub('<[^<]+?>', '', text)

    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def generate_replies(
    company_docs: Dict[str, str],
    posts: List[Dict[str, Any]],
    min_relevance: int = 5,
    model: str = "openai/gpt-4o-mini",
    own_account_id: str = None
) -> List[Reply]:
    """
    Generate replies to multiple posts at once using structured outputs

    Args:
        company_docs: Dictionary of company documentation
        posts: List of post dictionaries from Mastodon
        min_relevance: Minimum relevance score to actually reply (1-10)
        model: OpenRouter model to use

    Returns:
        List of Reply objects
    """
    client = create_llm_client()

    # Prepare company context (abbreviated)
    company_summary = f"""
Company: InventoryVision AI

Overview: {company_docs.get('01_company_overview', '')[:800]}

Brand Voice: Professional but approachable. We're experts in computer vision and retail technology,
but we're humble and focus on providing genuine value. We don't spam or oversell.
"""

    # Prepare posts for analysis
    posts_text = ""
    post_map = {}  # Map for easy lookup

    for i, post in enumerate(posts):
        post_id = post['id']
        post_map[post_id] = post

        author = post['account']['acct']
        content = clean_html(post['content'])
        created = post['created_at'].strftime("%Y-%m-%d %H:%M")

        posts_text += f"""
---
POST ID: {post_id}
Author: @{author}
Created: {created}
Content:
{content[:500]}
---
"""

    system_prompt = """You are a social media engagement specialist for InventoryVision AI.
Your job is to identify relevant posts and generate thoughtful, valuable replies.

Guidelines for replies:
1. ONLY reply if we can add genuine value to the conversation
2. Don't be salesy or promotional - be helpful and authentic
3. Share relevant insights or ask thoughtful questions
4. Keep replies brief (1-3 sentences)
5. Be professional but friendly
6. If the post is not relevant or we can't add value, set should_reply=False

Reply when:
- The post discusses retail technology, inventory management, or related topics
- We can provide helpful insights or perspectives
- The conversation is substantive and professional

Don't reply when:
- The post is off-topic
- It's spam or low-quality content
- We would just be promoting ourselves without adding value
- The conversation is too casual or personal
"""

    user_prompt = f"""Company Context:
{company_summary}

Analyze these posts and generate appropriate replies:
{posts_text}

For each post:
1. Assess its relevance to our company and expertise (1-10 score)
2. Determine if we should reply (only if we can add genuine value)
3. If yes, write a brief, helpful reply (1-3 sentences)
4. Explain your reasoning

Focus on building authentic connections, not just promotion."""

    print(f"Analyzing {len(posts)} posts for reply opportunities...")

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=BatchReplies,
    )

    batch = response.choices[0].message.parsed

    # Filter by relevance threshold
    relevant_replies = [
        reply for reply in batch.replies
        if reply.relevance_score >= min_relevance
    ]

    print(f"✓ Generated {len(batch.replies)} potential replies")
    print(f"✓ {len(relevant_replies)} meet relevance threshold ({min_relevance}/10)")
    print(f"✓ {sum(1 for r in relevant_replies if r.should_reply)} recommended to post")

    return relevant_replies


def display_reply_plan(replies: List[Reply]):
    """
    Display a summary of the reply plan

    Args:
        replies: List of Reply objects
    """
    print("\n" + "="*70)
    print("REPLY PLAN")
    print("="*70)

    for i, reply in enumerate(replies, 1):
        status = "✓ REPLY" if reply.should_reply else "✗ SKIP"
        print(f"\n{i}. Post ID: {reply.post_id} | Relevance: {reply.relevance_score}/10 | {status}")
        print(f"   Reasoning: {reply.reasoning}")

        if reply.should_reply:
            print(f"   Reply: \"{reply.reply_content}\"")

    print("\n" + "="*70)


if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    from mastodon_client import MastodonClient
    from post_generator import load_company_docs

    load_dotenv()

    try:
        # Load company docs
        print("Loading company documentation...")
        docs = load_company_docs()

        # Connect to Mastodon
        print("\nConnecting to Mastodon...")
        mastodon = MastodonClient()

        # Search for relevant posts
        print("\nSearching for posts about 'retail technology'...")
        posts = mastodon.search_posts("retail technology", limit=5)

        if not posts:
            print("No posts found. Try a different search term.")
        else:
            # Generate replies
            print(f"\nAnalyzing {len(posts)} posts...")
            replies = generate_replies(docs, posts, min_relevance=5)

            # Display plan
            display_reply_plan(replies)

            # Ask for confirmation before posting
            print("\n" + "="*70)
            should_post = input("Post these replies? (yes/no): ").strip().lower()

            if should_post == "yes":
                for reply in replies:
                    if reply.should_reply:
                        print(f"\nPosting reply to {reply.post_id}...")
                        mastodon.reply(reply.post_id, reply.reply_content)
                print("\n✓ All replies posted!")
            else:
                print("\nReply posting cancelled.")

    except ValueError as e:
        print(f"\nSetup required: {e}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

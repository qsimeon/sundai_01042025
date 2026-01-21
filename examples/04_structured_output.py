#!/usr/bin/env python3
"""
Example 4: Structured Outputs with Pydantic
Learn: How to get AI to return data in a specific format

Run: uv run python examples/04_structured_output.py
"""

import os
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

print("=" * 60)
print("EXAMPLE 4: Structured Outputs with Pydantic")
print("=" * 60)

# Step 1: Define the structure we want
print("\n📋 Step 1: Defining data structure...")


class BlogPost(BaseModel):
    """
    This defines what we want from the AI.
    Pydantic ensures the AI returns exactly this structure.
    """
    title: str = Field(description="Catchy blog post title")
    content: str = Field(description="Main blog post content (2-3 paragraphs)")
    tags: list[str] = Field(description="3-5 relevant tags")
    word_count: int = Field(description="Approximate word count")


print("✓ Defined BlogPost structure:")
print("  - title (string)")
print("  - content (string)")
print("  - tags (list of strings)")
print("  - word_count (integer)")

# Step 2: Load API key
print("\n📁 Step 2: Loading API key...")
load_dotenv(override=True)
api_key = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
print("✓ Connected to OpenRouter")

# Step 3: Ask AI with structured output
print("\n🤖 Step 3: Asking AI to generate blog post...")
print("(AI must follow our structure!)")

response = client.beta.chat.completions.parse(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You write blog posts about technology."},
        {"role": "user", "content": "Write a blog post about how AI is changing retail inventory management."}
    ],
    response_format=BlogPost  # This enforces our structure!
)

# Step 4: Get structured result
print("\n📊 Step 4: Received structured response!")
post = response.choices[0].message.parsed

# Now we can access fields directly!
print("\n" + "=" * 60)
print(f"TITLE: {post.title}")
print("=" * 60)
print(f"\n{post.content}\n")
print("-" * 60)
print(f"Tags: {', '.join(post.tags)}")
print(f"Word count: {post.word_count}")
print("=" * 60)

# Step 5: Show the power of structured data
print("\n💪 Step 5: Using structured data programmatically...")
print(f"✓ Title length: {len(post.title)} characters")
print(f"✓ Content length: {len(post.content)} characters")
print(f"✓ Number of tags: {len(post.tags)}")
print(f"✓ First tag: #{post.tags[0]}")

# We can also convert to dict or JSON
print("\n📦 As dictionary:")
print(post.model_dump())

print("\n" + "=" * 60)
print("✅ Example complete!")
print("\n💡 Compare this to unstructured output:")
print("   Without Pydantic: 'Title: My Post\\nContent: Here is...\\nTags: AI, tech'")
print("   With Pydantic: post.title, post.content, post.tags (clean access!)")
print("\n💡 Try creating your own structure:")
print("   - Recipe (ingredients, steps, time)")
print("   - Product (name, price, description, specs)")
print("   - SocialMediaPost (what we use in the main code!)")
print("=" * 60)

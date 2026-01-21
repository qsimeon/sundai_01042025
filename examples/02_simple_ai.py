#!/usr/bin/env python3
"""
Example 2: Simple AI Post Generation
Learn: How to use OpenRouter/OpenAI API for text generation

Run: uv run python examples/02_simple_ai.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

print("=" * 60)
print("EXAMPLE 2: Simple AI Post Generation")
print("=" * 60)

# Step 1: Load API key
print("\n📁 Step 1: Loading OpenRouter API key...")
load_dotenv(override=True)
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("❌ Error: OPENROUTER_API_KEY not found in .env")
    exit(1)

print(f"✓ API key loaded: {api_key[:20]}...")

# Step 2: Create OpenAI client (works with OpenRouter!)
print("\n🔌 Step 2: Connecting to OpenRouter...")
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"  # This makes it use OpenRouter
)
print("✓ Connected!")

# Step 3: Craft a prompt
print("\n📝 Step 3: Creating prompt...")
system_prompt = "You write short, engaging social media posts."
user_prompt = "Write a post about AI in retail. Max 100 words. Include 2-3 hashtags."

print(f"System: {system_prompt}")
print(f"User: {user_prompt}")

# Step 4: Call the AI
print("\n🤖 Step 4: Asking AI to generate post...")
print("(This might take a few seconds...)")

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",  # Fast and cheap model
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)

# Step 5: Get the result
print("\n📊 Step 5: AI generated:")
post = response.choices[0].message.content
print("\n" + "-" * 60)
print(post)
print("-" * 60)

print("\n" + "=" * 60)
print("✅ Example complete!")
print("\n💡 Try changing the prompt on line 34 to generate different posts")
print("   Examples:")
print("   - 'Write a poem about coding'")
print("   - 'Explain APIs in simple terms'")
print("   - 'Write a LinkedIn post about your startup'")
print("=" * 60)

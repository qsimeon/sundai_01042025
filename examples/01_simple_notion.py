#!/usr/bin/env python3
"""
Example 1: Simple Notion API Call
Learn: How to connect to an API and fetch data

Run: uv run python examples/01_simple_notion.py
"""

import os
from notion_client import Client
from dotenv import load_dotenv

print("=" * 60)
print("EXAMPLE 1: Simple Notion API Call")
print("=" * 60)

# Step 1: Load secrets from .env file
print("\n📁 Step 1: Loading secrets from .env...")
load_dotenv(override=True)
token = os.getenv("NOTION_INTEGRATION")

if not token:
    print("❌ Error: NOTION_INTEGRATION not found in .env")
    exit(1)

print(f"✓ Token loaded: {token[:20]}...")

# Step 2: Create a Notion client
print("\n🔌 Step 2: Connecting to Notion API...")
notion = Client(auth=token)
print("✓ Connected!")

# Step 3: Search for pages
print("\n🔍 Step 3: Searching for pages...")
results = notion.search(query="Company")

# Step 4: Print results
print(f"\n📊 Step 4: Found {len(results['results'])} pages:")
for i, page in enumerate(results["results"], 1):
    # Extract title from page properties
    props = page["properties"]
    for prop_name, prop_value in props.items():
        if prop_value["type"] == "title":
            title_array = prop_value.get("title", [])
            if title_array:
                title = title_array[0]["plain_text"]
                print(f"  {i}. {title}")
                break

print("\n" + "=" * 60)
print("✅ Example complete!")
print("\n💡 Try changing the query on line 32 to search for different pages")
print("=" * 60)

"""
Notion Document Loader
Fetches company documentation from Notion using the Notion API
"""

import os
from notion_client import Client
from typing import Dict


def load_company_docs_from_notion() -> Dict[str, str]:
    """
    Load company documentation from Notion workspace.

    Returns:
        Dictionary mapping document names to their content
    """
    notion_token = os.getenv("NOTION_INTEGRATION")
    if not notion_token:
        raise ValueError("NOTION_INTEGRATION not found in environment variables")

    # Initialize Notion client
    notion = Client(auth=notion_token)

    print("Connecting to Notion...")

    # First, try to get ALL accessible pages to see what we have
    print("Searching for all accessible pages...")
    all_results = notion.search(filter={"property": "object", "value": "page"})

    print(f"Found {len(all_results.get('results', []))} total accessible pages")

    # Try multiple search strategies
    search_queries = [
        "Company: Inventory.ai",
        "Inventory.ai",
        "InventoryVision",
        "company",
        ""  # Empty query returns all accessible pages
    ]

    all_pages = []
    for query in search_queries:
        if query:
            print(f"Searching for: '{query}'...")
            search_results = notion.search(
                query=query,
                filter={"property": "object", "value": "page"}
            )
        else:
            search_results = all_results

        results = search_results.get("results", [])
        print(f"  Found {len(results)} pages")

        for page in results:
            if page["id"] not in [p["id"] for p in all_pages]:
                all_pages.append(page)

        if all_pages:
            break  # Stop if we found something

    print(f"\nTotal unique pages found: {len(all_pages)}")

    docs = {}

    for page in all_pages:
        page_id = page["id"]

        # Get page title
        title = "Untitled"
        if page.get("properties"):
            # Try to get title from properties
            for prop_name, prop_value in page["properties"].items():
                if prop_value.get("type") == "title":
                    title_array = prop_value.get("title", [])
                    if title_array:
                        title = title_array[0].get("plain_text", "Untitled")
                    break

        # Retrieve page content (blocks)
        blocks = notion.blocks.children.list(block_id=page_id)

        # Extract text from blocks
        content_parts = []
        for block in blocks.get("results", []):
            block_type = block.get("type")
            block_content = block.get(block_type, {})

            # Extract text from different block types
            if "rich_text" in block_content:
                for text_obj in block_content["rich_text"]:
                    content_parts.append(text_obj.get("plain_text", ""))

            # Handle other block types
            elif block_type == "child_page":
                # Skip child pages for now
                pass

        content = "\n".join(content_parts).strip()

        if content:
            # Use title as key (clean it up for dict key)
            doc_key = title.lower().replace(" ", "_").replace(":", "")
            docs[doc_key] = content
            print(f"✓ Loaded: {title}")

    if not docs:
        raise ValueError(
            "\n❌ No documents found in Notion!\n\n"
            "Your integration is connecting, but can't access any pages.\n"
            "This usually means you haven't shared the pages with your integration.\n\n"
            "To fix this:\n"
            "1. Open Notion and go to your 'Company: Inventory.ai' page\n"
            "2. Click the '•••' menu (top right)\n"
            "3. Select 'Add connections'\n"
            "4. Choose your integration and click 'Confirm'\n"
            "5. Repeat for each page you want to use\n\n"
            "📖 See docs/NOTION_SETUP.md for detailed instructions"
        )

    print(f"\nLoaded {len(docs)} documents from Notion")
    return docs


if __name__ == "__main__":
    # Test the Notion loader
    from dotenv import load_dotenv
    load_dotenv()

    try:
        docs = load_company_docs_from_notion()
        print("\n" + "="*60)
        print("NOTION DOCUMENTS")
        print("="*60)
        for name, content in docs.items():
            print(f"\n{name}:")
            print(f"{content[:200]}..." if len(content) > 200 else content)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

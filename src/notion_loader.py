"""
Notion Document Loader
Fetches company documentation from Notion using the Notion API with recursive child page support
"""

import os
from notion_client import Client
from typing import Dict, List


def extract_page_content(notion: Client, page_id: str) -> str:
    """
    Extract text content from a Notion page.

    Args:
        notion: Notion client
        page_id: Page ID to extract content from

    Returns:
        Plain text content of the page
    """
    blocks = notion.blocks.children.list(block_id=page_id)

    content_parts = []
    for block in blocks.get("results", []):
        block_type = block.get("type")
        block_content = block.get(block_type, {})

        # Extract text from different block types
        if "rich_text" in block_content:
            for text_obj in block_content["rich_text"]:
                content_parts.append(text_obj.get("plain_text", ""))

    return "\n".join(content_parts).strip()


def get_page_title(page: dict) -> str:
    """
    Extract title from a Notion page object.

    Args:
        page: Page object from Notion API

    Returns:
        Page title or "Untitled"
    """
    title = "Untitled"

    if page.get("properties"):
        # Try to get title from properties
        for prop_name, prop_value in page["properties"].items():
            if prop_value.get("type") == "title":
                title_array = prop_value.get("title", [])
                if title_array:
                    title = title_array[0].get("plain_text", "Untitled")
                break

    return title


def get_child_pages(notion: Client, parent_id: str) -> List[dict]:
    """
    Recursively get all child pages under a parent page.

    Args:
        notion: Notion client
        parent_id: Parent page ID

    Returns:
        List of child page objects
    """
    child_pages = []

    # Get all blocks (children) of this page
    blocks = notion.blocks.children.list(block_id=parent_id)

    for block in blocks.get("results", []):
        # Check if this block is a child_page
        if block.get("type") == "child_page":
            page_id = block["id"]

            # Fetch the full page object to get properties
            try:
                page = notion.pages.retrieve(page_id=page_id)
                child_pages.append(page)

                # Recursively get children of this child page
                grandchildren = get_child_pages(notion, page_id)
                child_pages.extend(grandchildren)
            except Exception as e:
                print(f"  ⚠️  Could not fetch child page {page_id}: {e}")

    return child_pages


def load_company_docs_from_notion() -> Dict[str, str]:
    """
    Load company documentation from Notion workspace.
    Looks for a parent page (e.g., "Company: Inventory.AI") and recursively loads all child pages.

    Returns:
        Dictionary mapping document names to their content
    """
    notion_token = os.getenv("NOTION_INTEGRATION")
    if not notion_token:
        raise ValueError("NOTION_INTEGRATION not found in environment variables")

    # Initialize Notion client
    notion = Client(auth=notion_token)

    print("Connecting to Notion...")

    # Step 1: Find the parent "Company: Inventory.AI" page
    print("Searching for 'Company: Inventory.AI' parent page...")

    search_queries = [
        "Company: Inventory.AI",
        "Company: Inventory.ai",
        "Inventory.AI",
        "Company Inventory"
    ]

    parent_page = None
    for query in search_queries:
        print(f"  Trying: '{query}'...")
        search_results = notion.search(
            query=query,
            filter={"property": "object", "value": "page"}
        )

        results = search_results.get("results", [])
        if results:
            # Take the first result
            parent_page = results[0]
            parent_title = get_page_title(parent_page)
            print(f"  ✓ Found parent page: '{parent_title}'")
            break

    if not parent_page:
        # Try searching for all pages and let user know what we found
        print("\n⚠️  Could not find 'Company: Inventory.AI' page")
        print("Searching for all accessible pages...")
        all_results = notion.search(filter={"property": "object", "value": "page"})
        all_pages = all_results.get("results", [])

        if all_pages:
            print(f"\nFound {len(all_pages)} accessible page(s):")
            for page in all_pages:
                title = get_page_title(page)
                print(f"  - {title}")
            print("\nℹ️  Please make sure 'Company: Inventory.AI' is shared with your integration")
        else:
            print("\nℹ️  No pages are currently accessible to your integration")

        raise ValueError(
            "\n❌ Could not find 'Company: Inventory.AI' page!\n\n"
            "Make sure you have:\n"
            "1. Created a page called 'Company: Inventory.AI' in Notion\n"
            "2. Shared that page with your integration\n"
            "   (Click ••• menu → Add connections → Select your integration)\n\n"
            "📖 See docs/NOTION_SETUP.md for detailed instructions"
        )

    # Step 2: Get all child pages recursively
    print(f"\nFetching child pages under '{get_page_title(parent_page)}'...")
    child_pages = get_child_pages(notion, parent_page["id"])

    if not child_pages:
        print("\n⚠️  No child pages found under 'Company: Inventory.AI'")
        print("The parent page exists but has no nested documents.")
        print("\nMake sure:")
        print("  1. Your DOC 1, DOC 2, etc. are child pages (indented under the parent)")
        print("  2. Each child page is also shared with your integration")

        raise ValueError(
            "\n❌ No documents found!\n\n"
            "The 'Company: Inventory.AI' page exists but has no child pages.\n"
            "Please create child pages (DOC 1, DOC 2, etc.) under it and share them with your integration."
        )

    print(f"Found {len(child_pages)} nested document(s)")

    # Step 3: Extract content from each child page
    docs = {}

    for page in child_pages:
        page_id = page["id"]
        title = get_page_title(page)

        # Extract content
        content = extract_page_content(notion, page_id)

        if content:
            # Use title as key (clean it up for dict key)
            doc_key = title.lower().replace(" ", "_").replace(":", "").replace(".", "")
            docs[doc_key] = content
            print(f"  ✓ Loaded: {title} ({len(content)} chars)")
        else:
            print(f"  ⚠️  Skipped: {title} (no content)")

    if not docs:
        raise ValueError(
            "\n❌ No documents with content found!\n\n"
            "Child pages were found but they're all empty.\n"
            "Please add content to your DOC pages in Notion."
        )

    print(f"\n✅ Successfully loaded {len(docs)} documents from Notion")
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
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

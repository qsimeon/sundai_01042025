# Notion Integration Setup Guide

This branch uses Notion API to fetch company documentation instead of local files.

## Setup Steps

### 1. Verify Your Integration Token

Your integration token is already configured in `.env`:
```
NOTION_INTEGRATION=your_notion_integration_token_here
```

### 2. Share Pages with Your Integration

**IMPORTANT:** Notion integrations can only access pages that have been explicitly shared with them.

1. Open your Notion workspace (MIT PhD)
2. Navigate to your "Company: Inventory.ai" page
3. Click the "•••" menu in the top right
4. Select "Add connections"
5. Find and select your integration (it should match the token name)
6. Click "Confirm"

**You need to do this for EVERY page you want the integration to access.**

### 3. Page Structure

The code will automatically find and load all pages shared with the integration. You can organize them however you like:

```
📄 Company: Inventory.ai (parent page)
  ├─ 📄 Company Overview
  ├─ 📄 Product Description
  ├─ 📄 Technology & Architecture (High-Level)
  └─ 📄 Brand Voice & Social Media Constraint
```

### 4. Test the Integration

Run the test script to verify pages are accessible:

```bash
uv run python src/notion_loader.py
```

You should see output like:
```
Connecting to Notion...
Searching for all accessible pages...
Found 4 total accessible pages
✓ Loaded: Company Overview
✓ Loaded: Brand Voice
✓ Loaded: Products & Services
✓ Loaded: Target Audience

Loaded 4 documents from Notion
```

### 5. Use with Post Generator

Once pages are shared, the post generator will automatically use Notion:

```bash
./post_with_approval
./reply_with_approval "retail technology"
```

## Troubleshooting

### "Found 0 total accessible pages"

This means no pages have been shared with your integration. Go through Step 2 above for each page.

### "NOTION_INTEGRATION not found"

Make sure you have the `.env` file in the repo root with the integration token.

### Integration Not Showing Up

1. Go to https://www.notion.so/my-integrations
2. Verify your integration exists and is active
3. Check that it has the correct permissions (Read content)
4. Copy the Internal Integration Token and update `.env`

## Differences from Local Files

### Local Files (main branch)
- Docs stored in `company_docs/` directory
- Markdown files (*.md)
- Manual editing in text editor

### Notion (notion-integration branch)
- Docs stored in Notion workspace
- Rich text editing in Notion
- Easy to update from anywhere
- Supports collaboration
- Better for RAG (Retrieval Augmented Generation)

## RAG Benefits

Using Notion enables better RAG workflows:
- Semantic search across all documents
- Vector embeddings for relevant content retrieval
- Easy to add/update content without code changes
- Natural knowledge base for non-technical team members

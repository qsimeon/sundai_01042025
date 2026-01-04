# InventoryVision AI - Social Media Automation

## ✅ Workshop Complete!

All 4 goals from MIT 6.S093 Workshop 1 complete and tested.

## Quick Start

```bash
# Generate and post content
uv run python post thought_leadership

# Find and reply to relevant posts
uv run python reply "retail technology" 5
```

## Documentation

All documentation is in the [`docs/`](docs/) directory:

- **[docs/START_HERE.md](docs/START_HERE.md)** - Start here! Quick orientation
- **[docs/COMMANDS.md](docs/COMMANDS.md)** - All available commands
- **[docs/COMPLETE_GUIDE.md](docs/COMPLETE_GUIDE.md)** - Full story from concept to working system

## What This Does

1. **Generates posts** about InventoryVision AI (retail inventory tracking with VLM + SAM3D)
2. **Posts to Mastodon** automatically
3. **Finds relevant posts** by keyword
4. **Generates AI replies** using structured outputs
5. **Filters out self-posts** (doesn't reply to own posts)

## Commands

### Post Generation
```bash
uv run python post thought_leadership
uv run python post industry_insight
uv run python post product_update
uv run python post customer_story
```

### Reply Generation
```bash
# Basic usage
uv run python reply "retail technology" 5

# With different keyword and count
uv run python reply "inventory management" 10
```

### Full Workflow
```bash
uv run python src/main.py
```

## Successfully Posted

- https://mastodon.social/@qsimeon/115838250963515890
- https://mastodon.social/@qsimeon/115838259129156300

## Workshop Goals ✅

1. ✅ Created 5 company docs ([`company_docs/`](company_docs/))
2. ✅ LLM post generation with structured outputs
3. ✅ Mastodon integration (working!)
4. ✅ Reply generation with batch analysis (filters out self-posts)

## Technology

- OpenAI GPT-4o-mini ($0.002-0.005/post)
- Pydantic structured outputs
- Mastodon API
- Python 3.13 + uv

## Cost

~$0.003 per post (~0.3 cents). Very affordable!

## Documentation

For complete documentation, see [`docs/`](docs/) directory.

**Recommended reading order:**
1. [docs/START_HERE.md](docs/START_HERE.md)
2. [docs/COMMANDS.md](docs/COMMANDS.md)
3. [docs/COMPLETE_GUIDE.md](docs/COMPLETE_GUIDE.md)

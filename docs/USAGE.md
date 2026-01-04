# Quick Usage Guide

## ✅ Workshop Complete!
Successfully posted: https://mastodon.social/@qsimeon/115838250963515890

## Simple Commands

### Generate & Post (Recommended)
```bash
# Thought leadership post
uv run python post thought_leadership

# Industry insight
uv run python post industry_insight

# Product update
uv run python post product_update

# Customer story
uv run python post customer_story
```

### Full Interactive Workflow
```bash
# Generate post + find & reply to relevant posts
uv run python src/main.py
```

### Test Individual Components
```bash
# Test post generation only
uv run python src/post_generator.py

# Test Mastodon connection
uv run python src/mastodon_client.py

# Test reply generation
uv run python src/reply_generator.py
```

## What Was Fixed

### ✅ Character Limit
- Was: 1200+ characters (❌ rejected by Mastodon)
- Now: 350-400 characters (✅ works perfectly)

### ✅ OpenRouter Issues
**Problem**: Needed credits + rate limits on free tier

**Solution**: Using OpenAI GPT-4o-mini directly
- Cost: $0.002-0.005 per post (~0.2-0.5 cents)
- Reliable and fast
- No rate limits

## Workshop Goals Status

| Goal | Status | Details |
|------|--------|---------|
| 1. Create 3-5 company docs | ✅ | 5 comprehensive docs created |
| 2. LLM post generation | ✅ | Structured outputs + char limits |
| 3. Mastodon integration | ✅ | Posted successfully |
| 4. Reply generation | ✅ | Batch processing ready |

## Files Structure

```
sundai_01042025/
├── post                      # ⭐ Use this for quick posting
├── FINAL_SUMMARY.md          # Complete explanation
├── company_docs/             # Your 5 company documents
└── src/
    ├── post_generator.py     # Generate posts
    ├── reply_generator.py    # Generate replies
    ├── mastodon_client.py    # Mastodon API
    └── main.py               # Full workflow
```

## Example Output

```bash
$ uv run python post industry_insight

📚 Loading company docs...
Loaded 5 company documents
🤖 Generating industry_insight post...
✓ Generated post (327 characters)

============================================================
GENERATED POST
============================================================

In 2023, retailers faced a staggering $99 billion in inventory
shrinkage. The solution? Embrace technology! AI-driven inventory
tracking provides real-time insights, reducing errors and filling
shelves on time. Retailers leveraging such tech experience up to
60% less shrinkage. It's time to turn challenges into opportunities!

#RetailTech #InventoryLoss #AIinRetail

(367 characters)
============================================================

Post to Mastodon? (yes/no) [yes]: yes

📤 Posting to Mastodon...
✅ Posted: https://mastodon.social/@qsimeon/115838250963515890
```

## Cost
- Per post: ~$0.002-0.005 (0.2-0.5 cents)
- 100 posts: ~$0.50
- Very affordable! ✅

## Next Steps
1. Try different post types
2. Test reply generation: `uv run python src/reply_generator.py`
3. Run full workflow: `uv run python src/main.py`
4. Schedule daily posts with cron (optional)

## Need Help?
- Full details: See `FINAL_SUMMARY.md`
- Setup guide: See `QUICKSTART.md`
- Code docs: See `README.md`

## Congratulations! 🎉
You've completed MIT 6.S093 Workshop 1!

# Quick Reference Card

## 🚀 Essential Commands

```bash
# Test Telegram bot
uv run python test_telegram

# Test approval buttons
uv run python test_approval

# Post with Telegram approval (main workflow)
uv run python post_with_approval

# Reply with Telegram approval (each reply approved individually)
uv run python reply_with_approval "retail tech" 5

# Post directly (no approval)
uv run python post thought_leadership

# Generate replies with terminal approval only
uv run python reply "retail tech" 5
```

## 📱 Telegram Workflow

1. Run `uv run python post_with_approval`
2. Check Telegram for message with buttons
3. Press **✅ Approve** or **❌ Reject**
4. If approved → Posts to Mastodon
5. Get success notification with link

## 🔑 Setup Checklist

- [ ] Installed dependencies: `uv sync`
- [ ] Created `.env` file with API keys
- [ ] Got Telegram bot token from @BotFather
- [ ] Got Telegram chat ID
- [ ] Tested bot: `uv run python test_telegram`
- [ ] Tested approval: `uv run python test_approval`

## 📁 Key Files

```
src/
  post_generator.py      # AI post generation
  mastodon_client.py     # Post to Mastodon
  telegram_approval.py   # Button approval

post_with_approval       # Main command
test_approval            # Test buttons
.env                     # Your API keys
```

## 🐛 Quick Fixes

**Telegram not working?**
```bash
# Check credentials
cat .env | grep TELEGRAM

# Test again
uv run python test_telegram
```

**Character limit error?**
- Posts must be ≤500 chars
- System enforces 350 char content limit

**Package not found?**
```bash
uv sync
```

## 🎯 Post Types

- `thought_leadership` - Industry insights
- `product_update` - New features/updates
- `customer_story` - User success stories
- `industry_insight` - Market trends

## 💡 Tips

- Start with `test_approval` to test buttons
- Character count includes hashtags
- Replies auto-filter your own posts
- Timeout is 5 minutes for approval

## 📖 Full Documentation

See `docs/README.md` for comprehensive guide.

## 🆘 Help

- Workshop PDFs in `~/Downloads/`
- Telegram notebook: `Copy_of_telegram_bot_workshop.ipynb`
- Full README: `docs/README.md`

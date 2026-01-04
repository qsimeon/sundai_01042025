# START HERE 👋

## Welcome to InventoryVision AI Social Media Automation

This is a complete, working AI-powered social media system built for MIT 6.S093 Workshop 1.

### ✅ Status: All Goals Complete
- ✅ 5 company documents created
- ✅ LLM post generation working
- ✅ Posted to Mastodon successfully
- ✅ Reply generation with structured outputs working

### 🚀 Quick Start (30 seconds)

**Generate and post content:**
```bash
uv run python post thought_leadership
```

That's it! The system will:
1. Load your company docs
2. Generate a post with GPT-4o-mini
3. Show you the post
4. Post to Mastodon

### 📚 Documentation Guide

**Choose based on what you need:**

| Document | When to Read | Time |
|----------|-------------|------|
| **[COMMANDS.md](COMMANDS.md)** | Just want to run commands | 2 min |
| **[USAGE.md](USAGE.md)** | Quick reference | 3 min |
| **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** | Full story, all details | 15 min |
| **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** | Technical summary | 5 min |
| **[QUICKSTART.md](QUICKSTART.md)** | Setup from scratch | 5 min |
| **[README.md](README.md)** | For another LLM/agent | 10 min |

### 🎯 What You Can Do

#### 1. Generate Posts
```bash
uv run python post thought_leadership
uv run python post industry_insight
uv run python post product_update
uv run python post customer_story
```

#### 2. Full Workflow (Post + Replies)
```bash
uv run python src/main.py
```

#### 3. Test Components
```bash
uv run python src/post_generator.py      # Test generation
uv run python src/mastodon_client.py     # Test Mastodon
uv run python src/reply_generator.py     # Test replies
```

### 🏆 What We Built

**Company: InventoryVision AI**
- Uses VLMs + SAM3D for retail inventory tracking
- Turns security cameras into smart inventory managers
- 5 comprehensive company documents

**Technology:**
- OpenAI GPT-4o-mini for generation ($0.002-0.005/post)
- Pydantic for structured outputs (type-safe JSON)
- Mastodon API integration
- Batch reply generation with relevance scoring

**Successfully Posted:**
- https://mastodon.social/@qsimeon/115838250963515890
- https://mastodon.social/@qsimeon/115838259129156300

### ❓ Common Questions

**Q: Why didn't OpenRouter work?**
A: Needed credits ($0 balance) + free tier rate limited. OpenAI direct is cheaper and more reliable. See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) for full story.

**Q: How much does this cost?**
A: ~$0.003 per post (~0.3 cents). Very affordable!

**Q: How do I customize posts?**
A: Edit `src/post_generator.py` - change prompts, model, or limits.

**Q: Can I schedule daily posts?**
A: Yes! Use cron. See [COMMANDS.md](COMMANDS.md) for examples.

**Q: Did we complete all 4 workshop goals?**
A: Yes! ✅ All tested and working.

### 🔧 Troubleshooting

**Error: "OPENAI_API_KEY not found"**
```bash
cat .env | grep OPENAI_API_KEY
# If missing, add it to .env file
```

**Error: "Character limit exceeded"**
- Should be fixed (enforces 350 char limit)
- Try generating again (varies each time)

**Want more help?**
- See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - Troubleshooting section

### 📂 Project Structure

```
sundai_01042025/
├── START_HERE.md              ← You are here
├── COMMANDS.md                ← Quick command reference
├── COMPLETE_GUIDE.md          ← Full story & detailed guide
├── post                       ← Simple CLI (use this!)
├── company_docs/              ← 5 company documents
└── src/                       ← Source code
    ├── post_generator.py
    ├── reply_generator.py
    ├── mastodon_client.py
    └── main.py
```

### ✨ Next Steps

1. **Try it now:**
   ```bash
   uv run python post thought_leadership
   ```

2. **Read the full story:**
   Open [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)

3. **Customize for your needs:**
   - Edit prompts in `src/post_generator.py`
   - Change model or parameters
   - Add your own company docs

4. **Go further:**
   - Schedule daily posts
   - Track engagement
   - Add more platforms

### 🎓 Course Info

- **Course**: MIT 6.S093 - How to Ship Almost Anything with AI
- **Workshop**: Workshop 1 - Social Media Post Generator
- **Website**: https://iap.sundai.club
- **Date**: January 4, 2026

### 🙌 Success!

You have a complete, working, production-ready social media automation system!

**Try it now:**
```bash
uv run python post thought_leadership
```

Enjoy! 🚀

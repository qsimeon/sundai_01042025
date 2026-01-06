# MIT 6.S093 Workshop - Social Media AI Agent

**InventoryVision AI** - Automated social media posting with human-in-the-loop approval via Telegram

## 🎯 What This Does

This project implements a complete AI-powered social media agent for the MIT 6.S093 workshops that:

1. ✅ **Generates intelligent posts** using company documentation and AI (GPT-4o-mini)
2. ✅ **Posts to Mastodon** automatically
3. ✅ **Generates and posts replies** to relevant community posts
4. ✅ **Telegram approval workflow** - Human-in-the-loop checkpoint with button approval

## 🚀 Quick Start

### Test Telegram Bot
```bash
uv run python test_telegram
```

### Generate & Post with Approval
```bash
# Default post type (thought leadership)
uv run python post_with_approval

# Specific post type
uv run python post_with_approval product_update
```

You'll receive a message in Telegram with **✅ Approve** and **❌ Reject** buttons. Press one to approve or reject the post.

### Post Without Approval
```bash
uv run python post thought_leadership
```

### Generate Replies

**With Telegram Approval (Recommended):**
```bash
uv run python reply_with_approval "retail" 5
```
Finds posts, AI scores relevance (1-10), sends relevant ones to Telegram for approval before posting.

**Without Approval (Direct):**
```bash
uv run python reply "retail" 5
```
Finds 5 posts, AI scores relevance and shows scores, asks for approval in terminal (yes/no for all).

**Good keywords:** "retail", "inventory", "computer vision", "retail tech"
**Generic keywords:** "AI", "product marketing" (often not relevant to your niche)

## 📋 Requirements Met

### Workshop 1 ✅
- [x] Created 5 company documents
- [x] AI post generation with structured outputs
- [x] Mastodon integration
- [x] AI reply generation with batch analysis

### Workshop 2 ✅
- [x] Created Telegram bot
- [x] Implemented button-based approval workflow
- [x] Human-in-the-loop checkpoint

## 🏗️ Architecture

```
┌─────────────────────┐
│ Company Docs        │ (5 markdown files)
│ (InventoryVision)   │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ AI Post Generator   │ (GPT-4o-mini)
│ (Structured Output) │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Telegram Checkpoint │ ← 📱 Button Approval
│ (Human Approval)    │
└──────────┬──────────┘
           │ approved?
           v
┌─────────────────────┐
│ Mastodon Poster     │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ Success Notification│ ← 📱 Get link
└─────────────────────┘
```

## 📁 Project Structure

```
sundai_01042025/
├── src/
│   ├── post_generator.py          # AI post generation
│   ├── reply_generator.py         # AI reply generation
│   ├── mastodon_client.py         # Mastodon API
│   └── telegram_approval.py       # Telegram bot with buttons
├── company_docs/                  # 5 company docs
│   ├── 01_company_overview.md
│   ├── 02_technical_architecture.md
│   ├── 03_product_features.md
│   ├── 04_business_model.md
│   └── 05_brand_voice.md
├── docs/
│   ├── README.md                  # This file
│   └── QUICKSTART.md              # Quick reference
├── post_with_approval             # CLI: Post with Telegram approval
├── reply_with_approval            # CLI: Reply with Telegram approval (NEW!)
├── post                           # CLI: Direct posting
├── reply                          # CLI: Generate replies (terminal)
├── test_telegram                  # Test Telegram notifications
├── test_approval                  # Test button approval
├── .env                           # API keys (not in git)
└── pyproject.toml                 # Dependencies
```

## 🔧 Setup

### 1. Install Dependencies

This project uses **uv** (a fast Python package manager):

```bash
uv sync
```

### 2. Configure API Keys

Create a `.env` file with:

```bash
# OpenAI (for post generation)
OPENAI_API_KEY=sk-proj-...

# Mastodon
MASTODON_ACCESS_TOKEN=...
MASTODON_API_BASE_URL=https://mastodon.social

# Telegram (from @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABC...
TELEGRAM_CHAT_ID=123456789
```

### 3. Get Telegram Credentials

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Message your bot, then visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Find your chat ID in the JSON response

## 💻 Commands

### Main Commands

| Command | Description |
|---------|-------------|
| `uv run python post_with_approval` | Generate post → Telegram approval → Post to Mastodon |
| `uv run python reply_with_approval "<keyword>" <count>` | Find posts → Generate replies → Telegram approval for EACH |
| `uv run python post <type>` | Generate and post directly (no approval) |
| `uv run python reply "<keyword>" <count>` | Find posts and generate replies (terminal approval) |

### Testing

| Command | Description |
|---------|-------------|
| `uv run python test_telegram` | Test Telegram notifications |
| `uv run python test_approval` | Test button approval workflow |

### Post Types

- `thought_leadership` (default)
- `product_update`
- `customer_story`
- `industry_insight`

## 📱 Telegram Approval Flow

1. **Generate Post**
   ```bash
   uv run python post_with_approval
   ```

2. **Check Telegram**
   You'll receive a message like:
   ```
   📝 Approval Request: POST

   Content:
   Transform retail inventory with AI! Our VLM + SAM3D
   solution uses security cameras for smart tracking.
   #RetailTech #AI

   Character count: 145/500

   Approve this post?

   [✅ Approve]  [❌ Reject]
   ```

3. **Press a Button**
   - ✅ Approve → Posts to Mastodon
   - ❌ Reject → Cancels (nothing posted)

4. **Get Success Notification**
   If approved, you'll receive:
   ```
   ✅ Post published successfully!

   https://mastodon.social/@sundai_bot/123456
   ```

## 🏢 About InventoryVision AI

The company documents describe a fictional company that uses:
- **VLM (Vision Language Models)** for semantic understanding
- **SAM3D** for 3D image segmentation
- Security cameras to create 3D renderings of store inventory
- Real-time tracking to reduce shrinkage and manual counting errors

## 🛠️ Tech Stack

- **AI**: OpenRouter (currently using `openai/gpt-4o-mini` - ~$0.003/post)
  - Access to 50+ models: GPT-4, Claude, Llama, Gemini, etc.
  - Set `USE_OPENROUTER=true` in `.env` to enable (currently enabled)
  - Change model in `src/post_generator.py` line 82 (see https://openrouter.ai/models)
- **Social Media**: Mastodon API
- **Messaging**: Telegram Bot API with button approval
- **Language**: Python 3.13
- **Package Manager**: uv
- **Key Libraries**: `openai`, `mastodon-py`, `python-telegram-bot`, `pydantic`

## 📊 Cost

- **AI**: ~$0.003 per post (using OpenAI GPT-4o-mini via OpenRouter)
- **Mastodon**: Free
- **Telegram**: Free
- **Total**: ~$0.003 per post (essentially free)

## 🔍 Example Workflow

```bash
$ uv run python post_with_approval

📝 Generating thought_leadership post...
Loaded 5 company documents
Generating thought_leadership post for mastodon using gpt-4o-mini...
✓ Generated post (329 characters)

✅ Post generated!

============================================================
Generated content:
Did you know traditional inventory systems can miss up to 65%
of discrepancies? Embracing AI can transform this: real-time
tracking via your existing cameras can enhance accuracy and
reduce shrinkage significantly.

#RetailTech #AI #InventoryManagement
============================================================

Character count: 367/500

📱 Sending to Telegram for approval...
📱 Approval request sent to Telegram!
⏳ Waiting for you to press a button in Telegram...
   (Check your phone/Telegram app)

# You press ✅ Approve in Telegram

✅ Approved by user!
✅ Posting to Mastodon...
✓ Connected to Mastodon as @sundai_bot
✓ Posted to Mastodon: https://mastodon.social/@sundai_bot/123

✅ Posted successfully!
URL: https://mastodon.social/@sundai_bot/123

# You receive success notification in Telegram
```

## 🐛 Troubleshooting

### Telegram not working?
- Make sure you messaged your bot first (send `/start`)
- Check `.env` has correct `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Test with: `uv run python test_telegram`

### Character limit errors?
- Posts are limited to 500 characters total
- Content is max 350 chars to leave room for hashtags
- The system automatically enforces this

### Mastodon auth issues?
- Get a new access token from https://mastodon.social/settings/applications
- Update `MASTODON_ACCESS_TOKEN` in `.env`

### OpenAI errors?
- Check your OpenAI API key has credits
- Verify `OPENAI_API_KEY` in `.env`

## 🎓 Learning Notes

### What is uv?
**uv** is a super-fast Python package manager (like `npm` for Python). When you run `uv sync`, it:
- Reads `pyproject.toml`
- Installs all dependencies
- Creates an isolated environment

It's much faster than `pip` and handles dependencies automatically.

### Structured Outputs
We use Pydantic models to enforce structured JSON responses from the AI:

```python
class SocialMediaPost(BaseModel):
    content: str
    hashtags: list[str]
    platform: str
    post_type: str
```

This ensures the AI always returns properly formatted data.

### Self-Post Filtering
The reply generator filters out your own posts:

```python
own_account_id = mastodon.get_account_info()['id']
other_posts = [p for p in posts if p['account']['id'] != own_account_id]
```

## 🚀 Next Steps (Optional)

1. **Image Generation**: Add Replicate FLUX for AI-generated images
2. **Scheduling**: Add cron jobs for automated posting
3. **Analytics**: Track engagement metrics
4. **Multi-platform**: Add Twitter/LinkedIn support

## 📝 Files Explained

### Core Modules (`src/`)

- **`post_generator.py`** - Uses OpenAI to generate posts based on company docs
- **`reply_generator.py`** - Analyzes posts and generates contextual replies
- **`mastodon_client.py`** - Handles all Mastodon API interactions
- **`telegram_approval.py`** - Telegram bot with button-based approval

### CLI Scripts

- **`post_with_approval`** - Main command with Telegram approval
- **`post`** - Direct posting without approval
- **`reply`** - Find and reply to relevant posts
- **`test_telegram`** - Test Telegram notifications
- **`test_approval`** - Test button approval workflow

### Documentation

- **`docs/README.md`** - This file (comprehensive guide)
- **`docs/QUICKSTART.md`** - Quick reference card

## 📄 License

MIT License - Created for MIT 6.S093 IAP Course

## 🎉 Success!

You've built a complete AI social media agent with:
- Intelligent content generation
- Human oversight via Telegram
- Automated community engagement
- Professional documentation

**Your posts:**
- https://mastodon.social/@sundai_bot

Happy posting! 🚀

# Learning Examples

These simplified examples help you understand how each piece of the system works.

## 📚 Examples

### 1️⃣ Simple Notion API
**File:** `01_simple_notion.py`
**Learn:** How to connect to Notion and fetch pages
**Run:** `uv run python examples/01_simple_notion.py`

**What it does:**
- Loads your Notion token
- Connects to Notion API
- Searches for pages containing "Company"
- Prints the page titles

### 2️⃣ Simple AI Generation
**File:** `02_simple_ai.py`
**Learn:** How to use OpenRouter/OpenAI to generate text
**Run:** `uv run python examples/02_simple_ai.py`

**What it does:**
- Connects to OpenRouter
- Sends a prompt to AI
- Gets back a generated social media post
- Shows you the result

### 3️⃣ Simple Telegram Bot
**File:** `03_simple_telegram.py`
**Learn:** How to send messages with Telegram Bot API
**Run:** `uv run python examples/03_simple_telegram.py`

**What it does:**
- Creates a Telegram bot instance
- Gets bot information
- Sends a test message to your Telegram
- Shows async/await in action

### 4️⃣ Structured Outputs
**File:** `04_structured_output.py`
**Learn:** How to use Pydantic for structured AI responses
**Run:** `uv run python examples/04_structured_output.py`

**What it does:**
- Defines a BlogPost structure with Pydantic
- Makes AI generate a blog post following that structure
- Shows how to access fields programmatically
- Demonstrates why structured outputs are powerful

## 🎯 Learning Path

**Start here:**
1. Read `docs/ARCHITECTURE_GUIDE.md` for the big picture
2. Run Example 1 (Notion) - See how APIs work
3. Run Example 2 (AI) - See how AI generation works
4. Run Example 3 (Telegram) - See async/await
5. Run Example 4 (Structured) - See why Pydantic is awesome

**Then:**
- Read the actual code in `src/` folder
- Compare simple examples to the full implementation
- Try modifying examples to do new things

## 💡 Experiments to Try

### Modify Example 1 (Notion):
- Change the search query to find different pages
- Print more information about each page (dates, IDs, etc.)
- Try to fetch content from a specific page

### Modify Example 2 (AI):
- Change the prompt to generate different types of content
- Try different models (see https://openrouter.ai/models)
- Ask for longer or shorter outputs

### Modify Example 3 (Telegram):
- Send multiple messages
- Try sending with different formatting (bold, italic, etc.)
- Send an image or file

### Modify Example 4 (Structured):
- Create your own Pydantic model (Recipe, Product, etc.)
- Add validation (e.g., word_count must be > 0)
- Make nested structures (BlogPost with multiple Sections)

## 🐛 Common Issues

### "Module not found"
```bash
# Make sure dependencies are installed
uv sync
```

### "NOTION_INTEGRATION not found"
- Make sure `.env` file exists in repo root
- Check that variable is set in `.env`
- Make sure you're running from repo root

### "Telegram bot not responding"
- Start a chat with your bot on Telegram first
- Make sure bot token is correct
- Check that chat ID is correct (your user ID)

### "OpenRouter API error"
- Check your API key is valid
- Make sure you have credits (check openrouter.ai)
- Try a different model

## 📖 Next Steps

Once you understand these examples:
1. Read `src/post_generator.py` - See full post generation
2. Read `src/notion_loader.py` - See recursive page loading
3. Read `src/telegram_approval.py` - See button handling
4. Try modifying the main scripts (`post_with_approval`)

## 🤔 Questions?

While running examples, ask yourself:
- What data is being sent to the API?
- What data comes back?
- How is error handling done?
- Where do secrets come from?
- What would happen if I changed X?

Experiment! The code won't break anything. Worst case, you can always `git checkout` to revert changes.

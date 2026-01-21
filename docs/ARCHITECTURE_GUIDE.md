# Architecture Guide: Social Media Bot from First Principles

## 🎯 What Does This Project Do?

**Simple version:** A bot that writes social media posts about your company and posts them to Mastodon after you approve them via Telegram.

**More detailed:** It reads company information from Notion, uses AI to generate posts, sends them to you for approval on Telegram, and posts approved content to Mastodon.

---

## 📊 System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR COMPUTER                            │
│                                                                   │
│  ┌─────────────────┐                                            │
│  │ ./post_with_    │  ← You run this command                    │
│  │    approval      │                                            │
│  └────────┬─────────┘                                            │
│           │                                                       │
│           ↓                                                       │
│  ┌─────────────────────────────────────────────────┐            │
│  │          Python Script Flow                      │            │
│  │  1. Load .env (read API keys)                   │            │
│  │  2. Fetch docs from Notion                      │            │
│  │  3. Generate post using OpenRouter              │            │
│  │  4. Send to Telegram for approval               │            │
│  │  5. Wait for button press                       │            │
│  │  6. Post to Mastodon if approved                │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                   │
└───────────┬───────────────────────────────────┬──────────────────┘
            │                                   │
            ↓                                   ↓
    ┌──────────────┐                   ┌──────────────┐
    │   Internet   │                   │   Internet   │
    └──────┬───────┘                   └──────┬───────┘
           │                                   │
    ┌──────┴────────────────────────┬─────────┴──────┬──────────────┐
    │                               │                 │              │
    ↓                               ↓                 ↓              ↓
┌────────┐                    ┌──────────┐      ┌──────────┐  ┌──────────┐
│ Notion │                    │OpenRouter│      │ Telegram │  │ Mastodon │
│   API  │                    │   API    │      │   Bot    │  │   API    │
└────────┘                    └──────────┘      └──────────┘  └──────────┘
    │                               │                 │              │
    ↓                               ↓                 ↓              ↓
[Your Docs]                  [AI Models]        [Your Phone]   [Your Posts]
```

---

## 🧱 Building Blocks (First Principles)

### 1. What is an API?

**API = Application Programming Interface**

Think of it like a restaurant:
- **You (your code):** The customer
- **API:** The waiter
- **Service (Notion/OpenRouter/etc):** The kitchen

You don't go into the kitchen. You tell the waiter what you want, and they bring it back.

**Example:**
```python
# You ask Notion API: "Give me my company docs"
response = notion.search(query="Company: Inventory.AI")

# Notion returns: Here's your data!
docs = response.get("results")
```

### 2. What is an API Token/Key?

**Token = Your ID Badge**

When you call an API, you need to prove who you are. A token is like an ID badge that says "I'm allowed to access this."

**Why they're secret:**
- If someone steals your token, they can pretend to be you
- They could post from your account, read your data, etc.
- That's why we keep them in `.env` (which is in `.gitignore`)

**Example tokens in your `.env`:**
```bash
NOTION_INTEGRATION=ntn_397711...    # Your Notion ID badge
OPENROUTER_API_KEY=sk-or-v1-...    # Your OpenRouter ID badge
MASTODON_ACCESS_TOKEN=uQtXOJX-...  # Your Mastodon ID badge
```

### 3. What is Environment Variables?

**Environment Variables = Secret Settings**

Instead of writing secrets in code (BAD):
```python
# ❌ NEVER DO THIS
token = "my-secret-token-12345"  # Now it's in git forever!
```

We use environment variables (GOOD):
```python
# ✅ Good - reads from .env file
token = os.getenv("MASTODON_ACCESS_TOKEN")
```

**The `.env` file:**
```bash
# This file is NOT in git (it's in .gitignore)
MASTODON_ACCESS_TOKEN=abc123...
OPENROUTER_API_KEY=xyz789...
```

**How it works:**
1. You create `.env` with your secrets
2. Code reads it with `load_dotenv(override=True)`
3. Secrets stay on your computer, never in git

### 4. What is JSON?

**JSON = JavaScript Object Notation**

A way to structure data that both humans and computers can read.

**Python dictionary (in your code):**
```python
post = {
    "content": "AI is transforming retail!",
    "hashtags": ["RetailTech", "AI"],
    "platform": "mastodon"
}
```

**JSON (sent over internet):**
```json
{
  "content": "AI is transforming retail!",
  "hashtags": ["RetailTech", "AI"],
  "platform": "mastodon"
}
```

They look similar! Python converts dictionaries ↔ JSON automatically.

---

## 🏗️ System Architecture

### Layer 1: Entry Points (What You Run)

```
./post_with_approval        # Main script for posting
./reply_with_approval       # Main script for replying
```

**What they do:**
1. Load environment variables (`.env`)
2. Call functions from other modules
3. Coordinate the whole workflow

**Code breakdown of `post_with_approval`:**
```python
#!/usr/bin/env python3

# 1. Import tools we need
from post_generator import load_company_docs, generate_post
from telegram_approval import request_approval
from mastodon_client import MastodonClient

# 2. Main function - the entry point
def main():
    # 3. Load secrets from .env
    load_dotenv(override=True)

    # 4. Get company docs from Notion
    docs = load_company_docs()

    # 5. Use AI to generate a post
    post = generate_post(docs, post_type="thought_leadership")

    # 6. Send to Telegram, wait for approval
    approved = request_approval(post.content)

    # 7. If approved, post to Mastodon
    if approved:
        mastodon = MastodonClient()
        mastodon.post(post.content)

# 8. Run main when script is executed
if __name__ == "__main__":
    main()
```

### Layer 2: Core Modules (The Workers)

#### 2.1 `notion_loader.py` - Gets Docs from Notion

**Job:** Fetch your company documentation from Notion

**How it works:**
```python
# 1. Create a client (connect to Notion)
notion = Client(auth=your_token)

# 2. Search for your parent page
results = notion.search(query="Company: Inventory.AI")
parent_page = results["results"][0]

# 3. Get all child pages (DOC 1, DOC 2, etc.)
blocks = notion.blocks.children.list(block_id=parent_page["id"])

# 4. Extract text from each child page
for block in blocks:
    if block["type"] == "child_page":
        page_content = extract_text(block)
        docs[page_title] = page_content
```

**Why recursive?**
```
Company: Inventory.AI          ← Parent page
  ├─ DOC 1: Overview           ← Child page (we want this)
  │   └─ Section A             ← Grandchild (we want this too!)
  ├─ DOC 2: Products           ← Child page
  └─ DOC 3: Brand Voice        ← Child page
```

The `get_child_pages()` function calls itself to find nested pages:
```python
def get_child_pages(parent_id):
    children = []
    blocks = notion.blocks.children.list(parent_id)

    for block in blocks:
        if block["type"] == "child_page":
            children.append(block)
            # Recursion! Call itself to get grandchildren
            grandchildren = get_child_pages(block["id"])
            children.extend(grandchildren)

    return children
```

#### 2.2 `post_generator.py` - AI Post Generation

**Job:** Use AI to write posts based on your company docs

**Key concept: Prompt Engineering**

You give the AI:
1. **System prompt:** "You are a social media expert for InventoryVision AI"
2. **User prompt:** "Write a post about retail technology"
3. **Context:** Your company docs
4. **Schema:** Structure for the response (Pydantic)

```python
# Define what we want back from AI
class SocialMediaPost(BaseModel):
    content: str           # The actual post text
    hashtags: list[str]    # List of hashtags
    platform: str          # Which platform
    post_type: str         # Type of post

# Call the AI
response = client.beta.chat.completions.parse(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an expert..."},
        {"role": "user", "content": "Write a post about..."}
    ],
    response_format=SocialMediaPost  # AI must return this structure
)

# Get structured response
post = response.choices[0].message.parsed
# Now 'post' has .content, .hashtags, .platform, etc.
```

**Why structured outputs?**
Without structure:
```
AI returns: "Here's a great post: 'AI is cool!' #AI #Tech"
You: How do I separate content from hashtags? Parse text? Ugh.
```

With structure (Pydantic):
```
AI returns: {
  "content": "AI is cool!",
  "hashtags": ["AI", "Tech"],
  ...
}
You: Perfect! post.content and post.hashtags
```

#### 2.3 `telegram_approval.py` - Human-in-the-Loop

**Job:** Send post to Telegram, wait for you to click Approve/Reject

**How async/await works:**

Normal code (synchronous):
```python
send_message()      # Do this
wait_for_response() # Then do this
post_to_mastodon()  # Then do this
```

Async code:
```python
await send_message()       # Start this, wait for it
await wait_for_response()  # While waiting, program can do other things
await post_to_mastodon()   # Continue when ready
```

**Why async for Telegram?**
```python
# 1. Send message with buttons
message = await bot.send_message(
    chat_id=your_chat_id,
    text="Approve this post?",
    reply_markup=buttons  # Approve/Reject buttons
)

# 2. Wait for button click (could be 30 seconds, could be 5 minutes)
while not self.approval_received:
    updates = await bot.get_updates()  # Check for clicks
    for update in updates:
        if update.callback_query:  # Someone clicked!
            self.approval_received = True
            self.user_approved = (update.callback_query.data == "approve")
    await asyncio.sleep(1)  # Check every second

# 3. Return result
return self.user_approved  # True or False
```

**Button clicks = Callback Queries**
```python
# Create buttons
keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("✅ Approve", callback_data="approve"),
        InlineKeyboardButton("❌ Reject", callback_data="reject")
    ]
])

# When user clicks, Telegram sends callback_query with data="approve" or "reject"
```

#### 2.4 `mastodon_client.py` - Social Media Posting

**Job:** Post approved content to Mastodon

```python
class MastodonClient:
    def __init__(self):
        # Connect to Mastodon with your token
        self.client = Mastodon(
            access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
            api_base_url="https://mastodon.social"
        )

    def post(self, content):
        # Send POST request to Mastodon API
        status = self.client.status_post(content)
        # Returns URL of posted status
        return status["url"]
```

**API call breakdown:**
```python
# Your code:
mastodon.status_post("Hello world!")

# Behind the scenes:
# 1. Python makes HTTP POST request:
POST https://mastodon.social/api/v1/statuses
Headers: {
    "Authorization": "Bearer YOUR_TOKEN"
}
Body: {
    "status": "Hello world!"
}

# 2. Mastodon server processes it
# 3. Mastodon sends back:
{
    "id": "115930649164270277",
    "url": "https://mastodon.social/@sundai_bot/115930649164270277",
    "content": "Hello world!",
    ...
}

# 4. Python gives you that data
```

---

## 🔄 Complete Data Flow

Let's trace what happens when you run `./post_with_approval`:

### Step 0: Setup
```
1. Python reads .env file
   NOTION_INTEGRATION=ntn_...
   OPENROUTER_API_KEY=sk-or-v1-...
   etc.

2. These become environment variables in your program
```

### Step 1: Fetch Company Docs
```
[Your Computer] → notion.search("Company: Inventory.AI") → [Notion API]
                ← {"results": [page_data]} ←

[Your Computer] → notion.blocks.children.list(page_id) → [Notion API]
                ← {"results": [child_pages]} ←

Result: docs = {
    "doc_1_company_overview": "Inventory.AI is...",
    "doc_2_product": "Our product...",
    ...
}
```

### Step 2: Generate Post
```
[Your Computer] → OpenRouter API
  Sending:
    - System prompt: "You are a social media expert..."
    - User prompt: "Write a post..."
    - Context: All your company docs
    - Model: gpt-4o-mini
    - Response format: SocialMediaPost schema

[OpenRouter] → [OpenAI servers]
              ← AI generates post ←

[Your Computer] ← OpenRouter API
  Receives: {
    "content": "AI is transforming retail...",
    "hashtags": ["RetailTech", "AI"],
    ...
  }
```

### Step 3: Request Approval
```
[Your Computer] → Telegram Bot API
  Sending:
    - chat_id: Your Telegram user ID
    - text: "Approve this post? ..."
    - buttons: [Approve, Reject]

[Telegram Server] → [Your Phone]
  Push notification: "New message from your bot"

[Your Phone] → You click "Approve" → [Telegram Server]

[Your Computer] ← Telegram Bot API
  Polling every second:
    "Any updates?" → "Yes! User clicked 'approve'"

Result: approved = True
```

### Step 4: Post to Mastodon
```
[Your Computer] → Mastodon API
  POST /api/v1/statuses
  Authorization: Bearer YOUR_TOKEN
  Body: {
    "status": "AI is transforming retail... #RetailTech #AI"
  }

[Mastodon Server]
  1. Verifies your token
  2. Creates post in database
  3. Adds to your followers' timelines

[Your Computer] ← Mastodon API
  Response: {
    "id": "115930649164270277",
    "url": "https://mastodon.social/@sundai_bot/...",
    ...
  }

Result: Post is live!
```

---

## 🔑 Key Concepts Explained

### 1. Synchronous vs. Asynchronous

**Synchronous (normal code):**
```python
# Each step waits for previous to finish
docs = fetch_docs()        # Wait 2 seconds
post = generate_post()     # Wait 3 seconds
result = post_to_mastodon() # Wait 1 second
# Total: 6 seconds
```

**Asynchronous:**
```python
# Can do multiple things "at once"
docs_task = asyncio.create_task(fetch_docs())
post_task = asyncio.create_task(generate_post())

# Both fetch simultaneously!
docs, post = await asyncio.gather(docs_task, post_task)
# Total: 3 seconds (overlapped)
```

**When to use async?**
- Waiting for network (APIs, web requests)
- Waiting for user input (Telegram buttons)
- NOT for CPU work (AI processing happens on OpenRouter's servers)

### 2. Object-Oriented Programming (Classes)

**Without classes:**
```python
# Global variables, messy
mastodon_client = None
telegram_bot = None

def setup_mastodon():
    global mastodon_client
    mastodon_client = connect()

def post():
    mastodon_client.post("Hello")
```

**With classes (what we use):**
```python
class MastodonClient:
    def __init__(self):
        # Each instance has its own client
        self.client = connect()

    def post(self, content):
        # Methods can access self.client
        self.client.status_post(content)

# Create instance
mastodon = MastodonClient()
mastodon.post("Hello")  # Clean!
```

**Why better?**
- Encapsulation: Data and functions together
- Multiple instances: Could have 2 Mastodon accounts
- Cleaner code: No global variables

### 3. Pydantic Models (Type Safety)

**Without Pydantic:**
```python
# AI might return anything!
post = ai_generate()
content = post["content"]  # KeyError if missing?
hashtags = post["hashtags"]  # What if it's a string not a list?
```

**With Pydantic:**
```python
class SocialMediaPost(BaseModel):
    content: str           # MUST be a string
    hashtags: list[str]    # MUST be a list of strings
    platform: str          # MUST be present

# AI is forced to follow this structure
post = response.choices[0].message.parsed
# Guaranteed to have .content, .hashtags, .platform
```

**Validation example:**
```python
# Try to create invalid post
try:
    post = SocialMediaPost(
        content=123,  # Wrong! Should be string
        hashtags="AI",  # Wrong! Should be list
    )
except ValidationError as e:
    print(e)  # Pydantic tells you what's wrong
```

### 4. Dependency Management (uv/pip)

**Why we need it:**
Your code depends on external libraries:
- `notion-client` - To talk to Notion
- `openai` - To talk to OpenRouter/OpenAI
- `python-telegram-bot` - For Telegram
- `Mastodon.py` - For Mastodon
- `pydantic` - For type validation

**Old way (pip):**
```bash
pip install notion-client
pip install openai
# ... repeat for each
```

**Modern way (uv):**
```bash
uv add notion-client  # Adds to pyproject.toml AND installs
```

**`pyproject.toml` = Your recipe:**
```toml
[project]
name = "social-media-bot"
dependencies = [
    "notion-client>=2.7.0",
    "openai>=1.0.0",
    ...
]
```

**`uv.lock` = Exact versions:**
Locks exact versions so everyone gets same results.

**Why this matters:**
```
You: "My code works!"
Friend: *tries your code* "It's broken!"
Reason: They have notion-client 1.0, you have 2.7

With uv.lock: Both get exactly version 2.7.0
```

---

## 🎓 Learn to Code: Hands-On Examples

### Example 1: Simple API Call

Let's write a minimal Notion client:

```python
# File: simple_notion_test.py
import os
from notion_client import Client
from dotenv import load_dotenv

# Load secrets
load_dotenv(override=True)
token = os.getenv("NOTION_INTEGRATION")

# Connect to Notion
notion = Client(auth=token)

# Search for pages
results = notion.search(query="Company")

# Print what we found
print(f"Found {len(results['results'])} pages")
for page in results["results"]:
    # Extract title from page properties
    props = page["properties"]
    for prop_name, prop_value in props.items():
        if prop_value["type"] == "title":
            title = prop_value["title"][0]["plain_text"]
            print(f"  - {title}")
```

**Try it:**
```bash
uv run python simple_notion_test.py
```

### Example 2: Prompt Engineering

Let's write a minimal AI post generator:

```python
# File: simple_ai_test.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

# Connect to OpenRouter
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Simple prompt
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You write short social media posts."},
        {"role": "user", "content": "Write a post about AI in retail, max 100 words."}
    ]
)

# Get the AI's response
post = response.choices[0].message.content
print("Generated post:")
print(post)
```

**Try it:**
```bash
uv run python simple_ai_test.py
```

### Example 3: Telegram Bot (Minimal)

```python
# File: simple_telegram_test.py
import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

async def send_message():
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    # Send a message
    await bot.send_message(
        chat_id=chat_id,
        text="Hello from Python! 🤖"
    )
    print("Message sent!")

# Run the async function
asyncio.run(send_message())
```

**Try it:**
```bash
uv run python simple_telegram_test.py
```

---

## 📚 Further Learning

### Learn More About:

**1. Python Basics**
- Functions: `def my_function():`
- Classes: `class MyClass:`
- Imports: `from module import function`
- Data types: `str`, `int`, `list`, `dict`

**2. APIs**
- HTTP methods: GET (retrieve), POST (create), PUT (update), DELETE (delete)
- Status codes: 200 (OK), 401 (Unauthorized), 404 (Not Found)
- Headers: Metadata like `Authorization: Bearer token`
- Request/Response cycle

**3. Async Programming**
- `async def` - Declares async function
- `await` - Waits for async operation
- `asyncio.run()` - Runs async function
- Useful for I/O-bound operations (network, files)

**4. Environment Variables**
- `.env` file - Stores secrets locally
- `.gitignore` - Prevents `.env` from going to git
- `load_dotenv()` - Loads `.env` into `os.environ`
- `os.getenv("VAR")` - Reads environment variable

**5. JSON & Data Structures**
- JSON: Text format for data exchange
- Python dict ↔ JSON conversion
- Nested structures: `data["user"]["name"]`
- Lists vs. dicts: `[1,2,3]` vs. `{"key": "value"}`

---

## 🔍 Debugging Tips

### Common Issues:

**1. "NOTION_INTEGRATION not found"**
```python
# Check if .env is loaded
print(os.getenv("NOTION_INTEGRATION"))
# If None, .env not loaded or variable not set
```

**2. "401 Unauthorized"**
```python
# Token is wrong or expired
# Solution: Generate new token from API provider
```

**3. "Telegram bot not responding"**
```python
# Check if bot token is correct:
print(os.getenv("TELEGRAM_BOT_TOKEN")[:20])

# Test connection:
bot = Bot(token=your_token)
me = await bot.get_me()
print(f"Bot username: {me.username}")
```

**4. "Module not found"**
```bash
# Install dependencies:
uv sync

# Or install specific package:
uv add package-name
```

### Debug Workflow:

1. **Print statements** - Classic but effective
   ```python
   print(f"Token: {token[:20]}...")
   print(f"Docs loaded: {len(docs)}")
   ```

2. **Try/except blocks** - Catch errors
   ```python
   try:
       result = risky_operation()
   except Exception as e:
       print(f"Error: {e}")
       import traceback
       traceback.print_exc()  # Full error details
   ```

3. **Test in isolation** - Break down problems
   ```python
   # Instead of running full script, test one piece:
   from notion_loader import load_company_docs_from_notion
   docs = load_company_docs_from_notion()
   print(docs.keys())
   ```

---

## 🎯 Next Steps to Learn

**Beginner:**
1. Read through `post_with_approval` line by line
2. Add `print()` statements to see what's happening
3. Modify the system prompt in `post_generator.py`
4. Change hashtags or post length limits

**Intermediate:**
1. Add a new post type (e.g., "customer_story")
2. Create a function to post to multiple platforms
3. Add error handling for API failures
4. Write unit tests for your functions

**Advanced:**
1. Implement RAG (Retrieval Augmented Generation)
2. Add vector embeddings for semantic search
3. Create a web dashboard to manage posts
4. Set up scheduled posting (cron jobs)

---

## 📖 Glossary

- **API:** Way for programs to talk to each other
- **Token:** Secret key to authenticate with an API
- **Async:** Code that can wait without blocking
- **JSON:** Text format for structured data
- **Environment Variable:** Setting stored outside code
- **Pydantic:** Library for data validation
- **Client:** Object that connects to an API
- **Endpoint:** Specific URL on an API (like `/api/v1/posts`)
- **Callback:** Function called when something happens
- **Polling:** Repeatedly checking for updates

---

**Ready to experiment?** Try modifying one of the simple examples above, or ask me to explain any specific part in more detail!

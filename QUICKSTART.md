# Quick Start Guide

## Setup (5 minutes)

### 1. Get Mastodon API Token

1. Go to https://mastodon.social/settings/applications
2. Click **"New Application"**
3. Application name: `InventoryVision AI Post Generator`
4. Scopes: Check **read** and **write**
5. Click **Submit**
6. Copy the **"Your access token"** value

### 2. Update .env File

```bash
# Edit .env file
nano .env

# Replace this line:
MASTODON_ACCESS_TOKEN=YOUR_MASTODON_ACCESS_TOKEN_HERE

# With your actual token:
MASTODON_ACCESS_TOKEN=your_actual_token_here
```

### 3. Test the Setup

```bash
# Test Mastodon connection
uv run python src/mastodon_client.py

# Should show:
# ✓ Connected to Mastodon as @qsimeon
# Account: @qsimeon
# ...
```

### 4. Generate Your First Post

```bash
# Test post generation
uv run python src/post_generator.py

# Should generate and display a post
```

### 5. Run Full Automation

```bash
# Run the complete workflow
uv run python src/main.py
```

## What Each Script Does

### `post_generator.py`
- Loads company documentation
- Uses LLM with structured outputs to generate posts
- Formats posts for different platforms

**Run standalone:**
```bash
uv run python src/post_generator.py
```

### `mastodon_client.py`
- Connects to Mastodon API
- Posts status updates
- Searches for posts
- Replies to posts

**Run standalone:**
```bash
uv run python src/mastodon_client.py
```

### `reply_generator.py`
- Searches for relevant posts
- Analyzes relevance using AI
- Generates thoughtful replies using structured outputs
- Filters by relevance score

**Run standalone:**
```bash
uv run python src/reply_generator.py
```

### `main.py`
Complete workflow:
1. Generate original post
2. Post to Mastodon (with confirmation)
3. Search for relevant posts
4. Generate AI replies
5. Review and post replies

**Run:**
```bash
uv run python src/main.py
```

## Workflow Example

```bash
$ uv run python src/main.py

======================================================================
       InventoryVision AI - Social Media Automation
======================================================================

📚 Loading company documentation...
Loaded 5 company documents

🔗 Connecting to Mastodon...
✓ Connected to Mastodon as @qsimeon

======================================================================
                    STEP 1: Generate Original Post
======================================================================

What type of post? (thought_leadership/product_update/industry_insight) [thought_leadership]:

🤖 Generating thought_leadership post...
✓ Generated post (245 characters)

----------------------------------------------------------------------
GENERATED POST:
----------------------------------------------------------------------
[AI-generated post content here]

#RetailTech #ComputerVision #InventoryManagement
----------------------------------------------------------------------

Post this to Mastodon? (yes/no) [yes]: yes

📤 Posting to Mastodon...
✓ Posted successfully: https://mastodon.social/@qsimeon/...

======================================================================
                    STEP 2: Engage with Community
======================================================================

Search keyword for relevant posts [retail technology]:
How many posts to analyze? [5]:

🔍 Searching for posts about 'retail technology'...
✓ Found 5 posts

🤖 Analyzing posts and generating replies...
✓ Generated 5 potential replies
✓ 3 meet relevance threshold (6/10)
✓ 2 recommended to post

[Reply plan displayed...]

💬 2 replies recommended

Post these replies? (yes/no/review) [review]:
```

## Tips

### Customizing Posts
Edit the prompts in `src/post_generator.py` to adjust:
- Tone and style
- Post length
- Content focus
- Call-to-action style

### Adjusting Reply Behavior
In `src/reply_generator.py`:
- Change `min_relevance` to be more/less selective
- Modify system prompt for different reply styles
- Adjust reply length in the prompt

### Scheduling Posts
Use cron (macOS/Linux) to run automatically:

```bash
# Edit crontab
crontab -e

# Post every day at 9am
0 9 * * * cd /Users/quileesimeon/sundai_01042025 && /Users/quileesimeon/.local/bin/uv run python src/main.py < input.txt >> logs/automation.log 2>&1
```

Create `input.txt` with your preferred answers:
```
thought_leadership
yes
retail technology
5
yes
```

## Troubleshooting

### "OPENROUTER_API_KEY not found"
```bash
# Check .env file
cat .env | grep OPENROUTER_API_KEY

# Should show your key
# If not, add it to .env
```

### "MASTODON_ACCESS_TOKEN not found" or "Please update MASTODON_ACCESS_TOKEN"
You need to create a Mastodon application and get the token. See Setup step 1.

### "Failed to authenticate with Mastodon"
- Double-check your access token
- Make sure you copied the entire token
- Verify the token has read/write permissions

### Rate Limiting
If you get rate limit errors:
- Add delays between operations
- Reduce number of posts to analyze
- Use the review mode to post selectively

## Next Steps

1. **Test with dry run**: Run all scripts individually first
2. **Review generated content**: Make sure posts match your brand
3. **Start small**: Post 1-2 times manually before automating
4. **Monitor engagement**: Track which posts perform best
5. **Iterate on prompts**: Adjust the system prompts based on results

## Advanced Usage

### Use Different LLM Models

Edit the model parameter in function calls:

```python
# In post_generator.py or reply_generator.py
model="anthropic/claude-3.5-sonnet"  # Current default
model="openai/gpt-4-turbo"           # OpenAI GPT-4
model="meta-llama/llama-3-70b"       # Open source alternative
```

See available models: https://openrouter.ai/models

### Generate Multiple Post Types

```python
from post_generator import load_company_docs, generate_post

docs = load_company_docs()

# Generate different post types
thought_post = generate_post(docs, post_type="thought_leadership")
product_post = generate_post(docs, post_type="product_update")
industry_post = generate_post(docs, post_type="industry_insight")
```

### Batch Post Generation

```python
# Generate a week's worth of posts
post_types = [
    "thought_leadership",
    "industry_insight",
    "product_update",
    "customer_story",
    "thought_leadership"
]

posts = [generate_post(docs, post_type=pt) for pt in post_types]

# Save for scheduling
import json
with open('scheduled_posts.json', 'w') as f:
    json.dump([p.dict() for p in posts], f, indent=2)
```

## Workshop Goals ✓

- [x] Goal 1: Create 3-5 company docs ✓ (5 comprehensive documents)
- [x] Goal 2: Use LLM to generate social media posts ✓ (post_generator.py)
- [x] Goal 3: Integrate with Mastodon ✓ (mastodon_client.py)
- [x] Goal 4: Generate replies with structured outputs ✓ (reply_generator.py)
- [ ] Goal 5 (Optional): Integrate other platforms (Twitter, LinkedIn)

Congratulations! You've completed the workshop. 🎉

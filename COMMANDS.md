# Command Reference

## Quick Commands (Use These!)

### Generate and Post
```bash
# Thought leadership post
uv run python post thought_leadership

# Industry insight post
uv run python post industry_insight

# Product update post
uv run python post product_update

# Customer story post
uv run python post customer_story
```

**What happens**: Generates post → Shows preview → Asks to post → Posts to Mastodon

### Full Workflow (Post + Replies)
```bash
uv run python src/main.py
```

**What happens**:
1. Generate and post original content
2. Search for relevant posts
3. Generate AI replies
4. Review and post replies

### Test Individual Components
```bash
# Test post generation only
uv run python src/post_generator.py

# Test Mastodon connection
uv run python src/mastodon_client.py

# Test reply generation
uv run python src/reply_generator.py
```

## Examples

### Example 1: Quick Post
```bash
$ uv run python post thought_leadership

📚 Loading company docs...
🤖 Generating thought_leadership post...
✓ Generated post (352 characters)

============================================================
GENERATED POST
============================================================

Did you know? Retail shrinkage costs the industry $112B annually...

#RetailTech #InventoryAI #BusinessTransformation

(402 characters)
============================================================

Post to Mastodon? (yes/no) [yes]: yes

📤 Posting to Mastodon...
✅ Posted: https://mastodon.social/@qsimeon/...
```

### Example 2: Full Workflow
```bash
$ uv run python src/main.py

STEP 1: Generate Original Post
What type of post? [thought_leadership]: industry_insight

[Generated post shown]
Post to Mastodon? yes
✅ Posted!

STEP 2: Engage with Community
Search keyword [retail technology]:
How many posts? [5]: 5

Found 5 posts
Analyzing posts...
✓ Generated 5 potential replies
✓ 1 recommended to post

[Reply plan shown]
Post these replies? (yes/no/review) [review]: yes
✅ All replies posted!
```

### Example 3: Reply Generation Only
```bash
$ uv run python src/reply_generator.py

Connecting to Mastodon...
✓ Connected as @qsimeon

Searching for 'retail technology'...
✓ Found 5 posts

Analyzing posts...
✓ Generated 5 potential replies
✓ 1 meet relevance threshold (5/10)
✓ 1 recommended to post

Post ID: 12345 | Relevance: 10/10 | ✓ REPLY
Reasoning: Directly discusses AI inventory tracking
Reply: "Absolutely! Embracing AI-driven..."

Post these replies? (yes/no): yes
✅ Posted!
```

## Non-Interactive Usage

For automation/scripting:
```bash
# Auto-confirm with echo
echo "yes" | uv run python post thought_leadership

# Or using input redirection
uv run python post thought_leadership < input.txt
```

Where `input.txt` contains:
```
yes
```

## Cost Per Command

| Command | Cost | Details |
|---------|------|---------|
| `post [type]` | $0.002-0.005 | ~0.2-0.5 cents per post |
| `reply_generator.py` | $0.003-0.008 | Analyzes 5 posts |
| `main.py` | $0.005-0.013 | Post + replies |

Very affordable! $0.50 gets you ~100 posts.

## Customization

### Change Model
Edit `src/post_generator.py`:
```python
def generate_post(
    ...
    model: str = "gpt-4o-mini"  # Change this
)
```

Available models:
- `gpt-4o-mini` (current, cheap, fast)
- `gpt-4o` (more expensive, better quality)
- `gpt-3.5-turbo` (cheapest, lower quality)

### Change Search Keyword
Edit `src/reply_generator.py`:
```python
# Line ~200
posts = mastodon.search_posts("retail technology", limit=5)
#                              ^^^^^^^^^^^^^^^^^ change this
```

### Adjust Relevance Threshold
Edit `src/reply_generator.py`:
```python
replies = generate_replies(docs, posts, min_relevance=6)
#                                       ^^^^^^^^^^^^^^ change this
```

- Lower number = more replies (less selective)
- Higher number = fewer replies (more selective)

## Troubleshooting Commands

### Check API Keys
```bash
# Check if keys are set
cat .env | grep API_KEY
```

### Test Connection
```bash
# Test Mastodon connection
uv run python src/mastodon_client.py

# Should show:
# ✓ Connected to Mastodon as @qsimeon
```

### Verify Character Count
```bash
# Generate without posting to check length
uv run python src/post_generator.py

# Check the "(XXX characters)" output
```

## Scheduling (Optional)

### Daily Post with Cron
```bash
# Edit crontab
crontab -e

# Add this line for daily 9am post:
0 9 * * * cd /Users/quileesimeon/sundai_01042025 && /Users/quileesimeon/.local/bin/uv run python post thought_leadership < /dev/null >> logs/automation.log 2>&1
```

Create logs directory:
```bash
mkdir -p logs
```

## Advanced Usage

### Multiple Posts
```bash
# Generate multiple post types
for type in thought_leadership industry_insight product_update; do
    uv run python post $type
done
```

### Save Post Without Posting
Modify `post` script to add a `--dry-run` option, or just say "no" when asked to post.

## Getting Help

- **Full story**: See `COMPLETE_GUIDE.md`
- **Setup**: See `QUICKSTART.md`
- **Detailed docs**: See `README.md`
- **Summary**: See `FINAL_SUMMARY.md`

## Status Check

Verify everything works:
```bash
# 1. Test post generation
uv run python src/post_generator.py

# 2. Test Mastodon
uv run python src/mastodon_client.py

# 3. Test reply generation
uv run python src/reply_generator.py

# 4. Quick post
uv run python post thought_leadership
```

All should work without errors ✅

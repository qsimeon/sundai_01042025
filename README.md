# InventoryVision AI - Social Media Post Generator Workshop

## 🎉 Workshop Complete! All 4 Goals Achieved

**Quick Start**: See [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md) for the full story from concept to working system.

## Project Overview

This project is part of **MIT 6.S093 - Workshop 1: Build a Social Media Post Generator**. The workshop teaches how to use LLMs (Large Language Models) to create an AI-powered social media automation system.

**Status**: ✅ All workshop goals complete and tested
- ✅ Goal 1: Created 5 comprehensive company docs
- ✅ Goal 2: LLM post generation with structured outputs
- ✅ Goal 3: Mastodon integration (successfully posted!)
- ✅ Goal 4: Reply generation with batch analysis

### Workshop Goals
1. Generate company documentation (real or fictional)
2. Use LLMs to generate social media posts based on company docs
3. Integrate with Mastodon to post content automatically
4. Search for relevant posts and generate AI-powered replies using structured outputs
5. (Optional) Expand to other social media platforms

## Company Concept: InventoryVision AI

### The Idea
InventoryVision AI is an AI-powered retail inventory tracking system that uses existing security camera infrastructure combined with advanced computer vision to automatically track store inventory in real-time.

### Core Technology
- **Vision Language Models (VLMs)**: For semantic understanding and product identification
- **SAM3D Image Segmentation**: For precise object isolation and 3D reconstruction
- **Multi-Camera Fusion**: Combining multiple camera feeds for complete coverage
- **3D Digital Twin**: Creating complete 3D models of retail spaces and products

### Key Value Propositions
1. **Zero Additional Hardware**: Uses existing security cameras
2. **Automated Tracking**: No manual scanning or counting required
3. **3D Visualization**: Complete spatial understanding of inventory
4. **Daily Reconciliation**: Automatic detection of changes (new stock, sold items, moved items)
5. **Shrinkage Detection**: AI-powered loss prevention
6. **Predictive Analytics**: Smart restocking alerts and trend analysis

### Target Market
- Small to medium retail stores (primary)
- Large retail chains (secondary)
- Warehouses and distribution centers (tertiary)

## Project Structure

```
sundai_01042025/
├── README.md                          # This file - project overview and instructions
├── .env                               # Environment variables (API keys) - DO NOT COMMIT
├── .gitignore                         # Git ignore file
├── company_docs/                      # Company documentation for LLM context
│   ├── 01_company_overview.md        # Mission, problem, solution, target market
│   ├── 02_technical_architecture.md  # Technical stack, system design, features
│   ├── 03_product_features.md        # Detailed product capabilities and benefits
│   ├── 04_business_model.md          # Revenue model, market analysis, GTM strategy
│   └── 05_brand_voice.md             # Brand personality, messaging, social media guidelines
├── src/                               # Source code
│   ├── post_generator.py             # Main social media post generator
│   ├── mastodon_client.py            # Mastodon API integration
│   └── reply_generator.py            # Automated reply generation
└── pyproject.toml                     # Python dependencies (uv)
```

## Company Documentation Created

Five comprehensive documentation files have been created in `company_docs/`:

### 1. Company Overview (`01_company_overview.md`)
- Mission statement and company description
- Problem statement and solution
- Target market and competitive advantages
- Company values

### 2. Technical Architecture (`02_technical_architecture.md`)
- Core technology stack (VLMs, SAM3D, multi-camera fusion)
- System architecture (edge, processing, application layers)
- Key technical features (continuous tracking, 3D library, reconciliation)
- Scalability, privacy, and security considerations
- Integration capabilities and API ecosystem

### 3. Product Features (`03_product_features.md`)
- 8 core features with detailed benefits
- Advanced analytics capabilities
- Integration features (POS, IMS)
- User experience and mobile apps
- Setup process and support

### 4. Business Model (`04_business_model.md`)
- SaaS subscription tiers (Starter, Professional, Enterprise)
- Additional revenue streams
- Market analysis (TAM, SAM, SOM)
- Competitive landscape and advantages
- Go-to-market strategy (4 phases)
- Customer acquisition channels
- Financial projections and funding requirements

### 5. Brand Voice & Messaging (`05_brand_voice.md`)
- Brand personality and voice characteristics
- Key messages for different audiences
- Content pillars and distribution strategy
- Social media strategy (LinkedIn, Twitter, Mastodon, YouTube)
- Writing guidelines (do's and don'ts)
- Sample social media posts
- Crisis communication guidelines
- Visual brand guidelines

## Account Setup

### OpenRouter
- **Status**: ✅ Account created, API key added to `.zshrc`
- **Purpose**: Unified API for accessing multiple LLM providers (GPT-4, Claude, etc.)
- **API Endpoint**: `https://openrouter.ai/api/v1`
- **Documentation**: https://openrouter.ai/docs

**Setup Instructions**:
```bash
# API key should be in .zshrc or .env file
export OPENROUTER_API_KEY="your-api-key-here"
```

### Mastodon
- **Status**: ✅ Account created
- **Account**: [@qsimeon@mastodon.social](https://mastodon.social/@qsimeon)
- **Purpose**: Social media platform for posting AI-generated content
- **API**: Mastodon provides a well-documented REST API

**Setup Instructions**:
1. Go to Settings → Development → New Application
2. Create an application with read/write permissions
3. Copy the access token to `.env` file

## Implementation Plan

### Phase 1: Environment Setup

#### Install uv (Python dependency manager)
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project
cd /Users/quileesimeon/sundai_01042025
uv init
```

#### Create `.env` file
```bash
# Create .env file (never commit this!)
cat > .env << 'EOF'
OPENROUTER_API_KEY=your_openrouter_api_key_here
MASTODON_ACCESS_TOKEN=your_mastodon_token_here
MASTODON_API_BASE_URL=https://mastodon.social
EOF
```

#### Create `.gitignore`
```bash
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
.venv/
.python-version
*.log
EOF
```

#### Install dependencies
```bash
uv add openai python-dotenv Mastodon.py pydantic
```

### Phase 2: LLM Post Generator Implementation

#### Create `src/post_generator.py`

Key components:
1. **Load company docs**: Read all markdown files from `company_docs/`
2. **Create LLM client**: Use OpenAI library with OpenRouter endpoint
3. **Generate posts**: Use structured outputs (Pydantic) for consistent format
4. **Post schema**: Define structure (content, hashtags, platform)

Example structure:
```python
from openai import OpenAI
from pydantic import BaseModel
import os
from pathlib import Path

class SocialMediaPost(BaseModel):
    content: str
    hashtags: list[str]
    platform: str
    post_type: str  # "announcement", "thought_leadership", "customer_story", etc.

def load_company_docs():
    """Load all company documentation files"""
    docs_dir = Path("company_docs")
    docs = {}
    for doc_file in docs_dir.glob("*.md"):
        with open(doc_file, 'r') as f:
            docs[doc_file.stem] = f.read()
    return docs

def generate_post(client, company_docs, post_type="thought_leadership"):
    """Generate a social media post using LLM"""

    # Combine all company docs into context
    context = "\n\n".join([f"# {name}\n{content}"
                           for name, content in company_docs.items()])

    system_prompt = """You are a social media expert creating posts for InventoryVision AI.
    Use the company documentation to create engaging, authentic posts that align with our brand voice.
    Focus on providing value, not just promoting."""

    user_prompt = f"""Based on this company documentation:

{context}

Create a {post_type} social media post for LinkedIn that:
- Is engaging and valuable to retail professionals
- Includes relevant hashtags
- Follows our brand voice (confident but humble, technical but accessible)
- Is 150-250 words
- Includes a clear call-to-action if appropriate"""

    response = client.beta.chat.completions.parse(
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=SocialMediaPost,
    )

    return response.choices[0].message.parsed
```

### Phase 3: Mastodon Integration

#### Create `src/mastodon_client.py`

Key components:
1. **Authenticate**: Use access token from `.env`
2. **Post content**: Create status updates (toots)
3. **Search**: Find posts by keyword
4. **Reply**: Create replies to existing posts

Example structure:
```python
from mastodon import Mastodon
import os

class MastodonClient:
    def __init__(self):
        self.client = Mastodon(
            access_token=os.getenv('MASTODON_ACCESS_TOKEN'),
            api_base_url=os.getenv('MASTODON_API_BASE_URL')
        )

    def post(self, content):
        """Post a status update (toot)"""
        status = self.client.status_post(content)
        return status

    def search_posts(self, query, limit=5):
        """Search for posts containing a keyword"""
        results = self.client.search_v2(query, result_type="statuses")
        return results['statuses'][:limit]

    def reply(self, post_id, content):
        """Reply to a post"""
        status = self.client.status_post(
            content,
            in_reply_to_id=post_id
        )
        return status
```

### Phase 4: Reply Generation with Structured Outputs

#### Create `src/reply_generator.py`

Key components:
1. **Search for relevant posts**: Find posts about retail, inventory, AI, etc.
2. **Generate multiple replies**: Use structured outputs to generate replies to multiple posts at once
3. **Pydantic schema**: Define structure for batch replies
4. **Post replies**: Automatically reply to selected posts

Example Pydantic schema:
```python
from pydantic import BaseModel

class Reply(BaseModel):
    post_id: str
    reply_content: str
    should_reply: bool  # AI decides if reply is appropriate
    reasoning: str  # Why or why not to reply

class BatchReplies(BaseModel):
    replies: list[Reply]
```

#### Implementation flow:
1. Search Mastodon for keyword (e.g., "retail inventory", "retail technology")
2. Get 5-10 recent posts
3. Send all posts to LLM with company context
4. LLM generates structured output with replies for each post
5. Filter for `should_reply=True`
6. Post appropriate replies

### Phase 5: Main Application

#### Create `src/main.py`

Orchestrates the entire workflow:
```python
import os
from dotenv import load_dotenv
from post_generator import generate_post, load_company_docs
from mastodon_client import MastodonClient
from reply_generator import generate_replies

def main():
    # Load environment variables
    load_dotenv()

    # Initialize clients
    company_docs = load_company_docs()
    mastodon = MastodonClient()

    # 1. Generate and post original content
    print("Generating social media post...")
    post = generate_post(company_docs, post_type="thought_leadership")
    print(f"Generated post:\n{post.content}\n")

    print("Posting to Mastodon...")
    status = mastodon.post(f"{post.content}\n\n{' '.join(['#' + tag for tag in post.hashtags])}")
    print(f"Posted: {status['url']}\n")

    # 2. Find relevant posts and generate replies
    print("Searching for relevant posts...")
    keyword = "retail technology"
    relevant_posts = mastodon.search_posts(keyword, limit=5)

    print(f"Found {len(relevant_posts)} posts about '{keyword}'")
    print("Generating replies...")

    replies = generate_replies(company_docs, relevant_posts)

    # 3. Post replies
    for reply in replies:
        if reply.should_reply:
            print(f"\nReplying to post {reply.post_id}")
            print(f"Reasoning: {reply.reasoning}")
            print(f"Reply: {reply.reply_content}")
            mastodon.reply(reply.post_id, reply.reply_content)
        else:
            print(f"\nSkipping post {reply.post_id}: {reply.reasoning}")

if __name__ == "__main__":
    main()
```

## Instructions for Another LLM/Agent

### Context
This is a workshop project (MIT 6.S093 Workshop 1) to build an AI-powered social media post generator. The company concept is **InventoryVision AI**, a retail inventory tracking system using computer vision and 3D reconstruction.

### What Has Been Done
1. ✅ Company idea refined and detailed business plan created
2. ✅ Five comprehensive company documentation files created in `company_docs/`
3. ✅ OpenRouter account set up with API key in environment
4. ✅ Mastodon account created: @qsimeon@mastodon.social

### What Needs to Be Done

#### Step 1: Set up Python environment
```bash
cd /Users/quileesimeon/sundai_01042025

# Initialize uv project
uv init

# Add dependencies
uv add openai python-dotenv Mastodon.py pydantic

# Create .env file
cat > .env << 'EOF'
OPENROUTER_API_KEY=<get from zshrc>
MASTODON_ACCESS_TOKEN=<need to create app in Mastodon settings>
MASTODON_API_BASE_URL=https://mastodon.social
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
.venv/
.python-version
*.log
EOF
```

#### Step 2: Get Mastodon API token
1. Go to https://mastodon.social/settings/applications
2. Click "New Application"
3. Application name: "InventoryVision AI Post Generator"
4. Scopes: read, write
5. Submit and copy the "Access Token"
6. Add to `.env` file

#### Step 3: Implement the code
Create the following files following the structure outlined in the "Implementation Plan" section above:
- `src/post_generator.py` - LLM-based post generation with structured outputs
- `src/mastodon_client.py` - Mastodon API wrapper
- `src/reply_generator.py` - Batch reply generation with structured outputs
- `src/main.py` - Main orchestration script

#### Step 4: Test and iterate
```bash
# Run the application
uv run python src/main.py

# This should:
# 1. Generate a social media post based on company docs
# 2. Post it to Mastodon
# 3. Search for relevant posts about retail technology
# 4. Generate intelligent replies using LLM
# 5. Post appropriate replies
```

#### Step 5: Refine prompts
- Adjust the system prompts to better match brand voice
- Experiment with different post types (thought leadership, customer stories, product updates)
- Fine-tune reply generation to be more engaging and less salesy

#### Step 6: (Optional) Expand platforms
- Add Twitter/X integration
- Add LinkedIn integration (requires OAuth)
- Add scheduling capabilities

## Key Technical Concepts from Workshop

### 1. OpenAI API Library with OpenRouter
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="anthropic/claude-3.5-sonnet",  # Can switch models easily
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
)
```

**Why**: Avoids vendor lock-in. Same API works with OpenAI, Anthropic, Google, etc. Just change base_url and model name.

### 2. Structured Outputs with Pydantic
```python
from pydantic import BaseModel

class SocialMediaPost(BaseModel):
    content: str
    hashtags: list[str]
    post_type: str

response = client.beta.chat.completions.parse(
    model="anthropic/claude-3.5-sonnet",
    messages=[...],
    response_format=SocialMediaPost
)

post = response.choices[0].message.parsed
# post is now a SocialMediaPost object with guaranteed structure
```

**Why**: Ensures LLM output matches expected format. No parsing errors, type-safe responses.

### 3. Mastodon API Integration
```python
from mastodon import Mastodon

client = Mastodon(
    access_token=os.getenv('MASTODON_ACCESS_TOKEN'),
    api_base_url='https://mastodon.social'
)

# Post
status = client.status_post("Hello from InventoryVision AI!")

# Search
results = client.search_v2("retail technology", result_type="statuses")

# Reply
client.status_post("Great point!", in_reply_to_id=original_post_id)
```

**Why**: Mastodon has free, open API (unlike Twitter). Good for testing before moving to other platforms.

### 4. Environment Variables for Secrets
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')
```

**Why**: Never commit API keys to git. `.env` file is in `.gitignore`.

## Troubleshooting

### Common Issues

#### 1. OpenRouter API Key Not Found
**Error**: `openai.AuthenticationError`
**Solution**:
```bash
# Check if key is in .env
cat .env | grep OPENROUTER_API_KEY

# Or get from zshrc
grep OPENROUTER_API_KEY ~/.zshrc

# Make sure to load_dotenv() in Python
```

#### 2. Mastodon Authentication Failed
**Error**: `MastodonUnauthorizedError`
**Solution**:
- Verify access token is correct
- Check that application has read/write permissions
- Verify base URL is correct (https://mastodon.social)

#### 3. Structured Output Parsing Failed
**Error**: `pydantic.ValidationError`
**Solution**:
- Check Pydantic model matches expected output
- Some models don't support structured outputs well - try Claude or GPT-4
- Add more detailed field descriptions in Pydantic model

#### 4. Rate Limiting
**Error**: `429 Too Many Requests`
**Solution**:
- Add delays between API calls (`time.sleep(2)`)
- Reduce number of posts/replies
- Check OpenRouter and Mastodon rate limits

## Next Steps After Workshop

### Enhancements
1. **Scheduling**: Use cron or GitHub Actions to post automatically
2. **Analytics**: Track engagement (likes, replies, retweets)
3. **A/B Testing**: Test different post formats and measure performance
4. **Multi-platform**: Expand to LinkedIn, Twitter, etc.
5. **Content Calendar**: Plan posts in advance with themes
6. **Image Generation**: Use DALL-E or Stable Diffusion for post images
7. **Engagement Analysis**: Analyze which topics perform best

### Production Considerations
1. **Error Handling**: Robust error handling and logging
2. **Monitoring**: Track API usage and costs
3. **Content Moderation**: Review AI-generated content before posting
4. **Rate Limiting**: Respect platform limits
5. **Backup**: Store generated content for records
6. **Analytics Dashboard**: Visualize performance metrics

## Resources

### Workshop Materials
- Workshop PDF: `/Users/quileesimeon/Downloads/Workshop 1.pdf`
- Workshop website: https://iap.sundai.club
- Course: MIT 6.S093 - How to Ship Almost Anything with AI

### Documentation
- **OpenRouter**: https://openrouter.ai/docs
- **OpenAI API**: https://platform.openai.com/docs
- **Pydantic**: https://docs.pydantic.dev
- **Mastodon API**: https://docs.joinmastodon.org/client/intro/
- **Mastodon.py**: https://mastodonpy.readthedocs.io

### Tools
- **uv**: https://github.com/astral-sh/uv
- **Claude Code**: AI-powered coding assistant (used to create this project)

## Project Metadata

- **Created**: January 4, 2026
- **Workshop**: MIT 6.S093 Workshop 1
- **Company**: InventoryVision AI (fictional, for workshop)
- **Mastodon**: [@qsimeon@mastodon.social](https://mastodon.social/@qsimeon)
- **Tech Stack**: Python, OpenAI API, OpenRouter, Pydantic, Mastodon.py, uv

---

## Memory Trace: Interaction Summary

### User's Initial Request
User wanted help with Workshop 1 from MIT 6.S093. They provided:
- **Company idea**: Use VLMs + SAM3D for retail inventory tracking via security cameras
- **Status**: Mastodon account created (@qsimeon), OpenRouter API key in zshrc
- **Request**: Refine idea, create company docs, create instructions/README

### Agent's Response
1. **Refined company concept** into detailed business plan for "InventoryVision AI"
2. **Created 5 comprehensive documentation files**:
   - Company overview (mission, problem/solution, market)
   - Technical architecture (VLMs, SAM3D, system design)
   - Product features (8 core features + analytics)
   - Business model (pricing, market analysis, GTM strategy)
   - Brand voice (personality, messaging, social media guidelines)
3. **Created this README** as instructions for future LLM/agent interactions
4. **Outlined implementation plan** for the workshop goals

### What Makes This Project Unique
- Real, innovative company concept (VLM + 3D segmentation for retail)
- Comprehensive documentation suitable for actual fundraising/development
- Complete brand voice and social media strategy
- Step-by-step instructions for implementation
- Focus on avoiding vendor lock-in (OpenRouter vs direct OpenAI/Anthropic)
- Privacy-first approach (inventory tracking, not surveillance)

### Next Agent Should
1. Help set up Python environment with uv
2. Create Mastodon API token
3. Implement the code files (post_generator.py, mastodon_client.py, reply_generator.py, main.py)
4. Test the complete workflow
5. Iterate on prompt engineering for better posts/replies

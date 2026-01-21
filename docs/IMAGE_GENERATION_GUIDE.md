# Image Generation with Custom Flux LoRA

## 🎨 Overview

Your social media bot now generates custom images using your fine-tuned Flux LoRA model from Replicate! Every post includes a unique image featuring your character in contexts related to the post content.

**Model:** `sundai-club/pikachu_sfw`
**Trigger Word:** `SFHO932`
**Platform:** Replicate API

---

## 🚀 How It Works

### Complete Workflow

```
1. Load company docs from Notion
   ↓
2. AI generates post text + image prompt
   Example: "character using AI tools in a retail store setting"
   ↓
3. Replicate generates image with your LoRA model
   Prompt becomes: "SFHO932 character using AI tools in a retail store setting"
   ↓
4. Send to Telegram WITH image preview
   You see exactly what will be posted
   ↓
5. You click "Approve" or "Reject"
   ↓
6. Post to Mastodon with image attached
```

### Generation Time
- **Post text:** ~2-3 seconds (OpenRouter GPT-4o-mini)
- **Image:** ~25-35 seconds (Replicate Flux)
- **Total:** ~30-40 seconds per post

---

## 📋 Usage

### Basic Post with Image
```bash
./post_with_approval
```

This will:
1. Generate a thought leadership post
2. Create a matching image with your character
3. Send both to Telegram for approval
4. Post to Mastodon if approved

### Specify Post Type
```bash
./post_with_approval product_update
./post_with_approval customer_story
./post_with_approval industry_insight
```

### Reply to Posts (No Images)
```bash
./reply_with_approval "retail technology"
```

Note: Replies don't include images for faster workflow.

---

## 🎯 Image Prompt Generation

The AI automatically creates image prompts based on your post content:

| Post Keywords | Generated Scene |
|---|---|
| retail, inventory | "character in a retail store with shelves" |
| technology, AI | "character with holographic displays" |
| automation | "character in automated warehouse" |
| camera, vision | "character looking at security camera" |
| data | "character surrounded by data visualizations" |

**All prompts include:**
- Your trigger word (`SFHO932`) - added automatically
- Professional lighting and quality modifiers
- Context relevant to InventoryVision AI business

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Replicate API (required for images)
REPLICATE_API_TOKEN=your_replicate_api_token_here
REPLICATE_MODEL=sundai-club/pikachu_sfw:a2d1104c23de51da6c1ad2b7918d8e4fc3d2b10678d32b2e482343d448f1c3ca
REPLICATE_TRIGGER_WORD=SFHO932
```

### Image Parameters

Edit `src/image_generator.py` to customize:

```python
# In generate_image() function
aspect_ratio="1:1",           # Square (good for social media)
num_inference_steps=28,        # Quality (4-50, higher=better)
guidance_scale=3.0,           # Prompt adherence (0-10)
output_format="png",          # png, jpg, or webp
output_quality=90,            # 1-100 (for jpg/webp)
```

**Recommended settings:**
- **Fast draft:** `num_inference_steps=4` (~10 sec, lower quality)
- **Balanced:** `num_inference_steps=28` (~30 sec, good quality) ← Current
- **High quality:** `num_inference_steps=50` (~50 sec, best quality)

---

## 📁 File Storage

### Generated Images Location
```
generated_images/
├── character_using_AI_tools_in_a_retail_store_setting.png
├── character_in_a_retail_store_analyzing_shelves_pro.png
└── ...
```

- **Saved locally** for records
- **Gitignored** (not committed to repository)
- **Filename** based on image prompt (sanitized)
- **Format:** PNG (high quality, transparency support)

### Cleanup
```bash
# Remove old images
rm generated_images/*.png

# Keep the directory
# (generated_images/.gitkeep ensures it stays in git)
```

---

## 🧪 Testing

### Test Image Generation Only
```bash
uv run python src/image_generator.py
```

This generates a test image without posting anything.

### Test Full Workflow
```bash
uv run python ./post_with_approval
```

Check Telegram for approval request with image preview.

### View Generated Images
```bash
open generated_images/
```

Or on Linux:
```bash
xdg-open generated_images/
```

---

## 💡 Customization Examples

### 1. Change Image Aspect Ratio

**Square (current):** `1:1` - Best for social media
**Landscape:** `16:9` - Better for hero images
**Portrait:** `4:5` - Instagram-style

Edit `post_with_approval`, line ~56:
```python
image_path = generate_image(
    prompt=post.image_prompt,
    aspect_ratio="16:9",  # Change this
    num_inference_steps=28,
)
```

### 2. Customize Image Prompts

Edit `src/image_generator.py`, function `generate_image_prompt()`:

```python
# Add your own keyword mappings
keywords = {
    "retail": "in a modern retail store with shelves",
    "warehouse": "in a large automated warehouse",
    "customer": "helping customers with a smile",
    # Add more...
}
```

### 3. Change Image Style

Modify prompts in `src/post_generator.py`, line ~20:

```python
image_prompt: str = Field(
    description="A concise visual prompt featuring a character in [YOUR STYLE HERE]. "
                "Examples: 'character in minimalist line art style' or 'character in photorealistic setting'"
)
```

---

## 📊 Cost & Performance

### Replicate Pricing
- **Model:** Flux.1 [dev] with LoRA
- **Cost:** ~$0.0015 per image (28 steps)
- **Estimated:** $0.15 per 100 posts

### OpenRouter (Text Generation)
- **Model:** GPT-4o-mini
- **Cost:** ~$0.003 per post
- **Estimated:** $0.30 per 100 posts

### Total Cost
**~$0.45 per 100 posts** (with images)

Compare to:
- Stock photos: $10-30 per image
- Designer: $50-200 per custom image
- AI with your branding: **$0.0045 per image** ✨

---

## 🐛 Troubleshooting

### "REPLICATE_API_TOKEN not found"
```bash
# Check .env file
grep REPLICATE .env

# Should show:
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

### Image Generation Fails
```python
# The script continues without images if generation fails
⚠️  Image generation failed: [error message]
Continuing without image...
```

**Common causes:**
- Invalid API token
- Replicate service temporarily down
- Network connectivity issues

**Solution:** Post will still work, just without image.

### Image Not Showing in Telegram
- **Check:** File exists in `generated_images/`
- **Check:** File size (should be 1-2 MB for PNG)
- **Fix:** Telegram may timeout on very large files, try JPG:
  ```python
  output_format="jpg",  # Instead of "png"
  output_quality=85,
  ```

### Images Look Wrong
- **Not matching style:** Check trigger word is in prompt
  ```bash
  # Should see in logs:
  Prompt: SFHO932 character in retail store...
  ```
- **Low quality:** Increase `num_inference_steps` (up to 50)
- **Wrong composition:** Adjust prompt in `generate_image_prompt()`

---

## 🎓 Advanced: Custom Prompting

### Prompt Engineering Tips

**Good prompts for your LoRA:**
```
✅ "SFHO932 character in modern office with laptop"
✅ "SFHO932 character analyzing data on screens"
✅ "SFHO932 character in warehouse with inventory"
```

**Less effective:**
```
❌ "A person in an office" (no trigger word)
❌ "SFHO932 flying through space" (too far from training data)
❌ "SFHO932 multiple characters interacting" (single character works best)
```

### Training Data Context

Your model was trained on Pikachu images, so it works best with:
- Single character focus
- Clear, well-lit scenes
- Professional/business contexts
- Tech/retail environments

---

## 🔄 Workflow Comparison

### Without Images (Old)
```
1. Generate post text (3 sec)
2. Telegram approval
3. Post to Mastodon
Total: ~10 seconds + your approval time
```

### With Images (New)
```
1. Generate post text (3 sec)
2. Generate image (30 sec)
3. Telegram approval with preview
4. Post to Mastodon with image
Total: ~35 seconds + your approval time
```

**Worth it?** Absolutely! Custom branded imagery makes your posts:
- More engaging (images get 2-3x more engagement)
- More professional (consistent visual identity)
- More memorable (your character becomes recognizable)

---

## 📚 Related Documentation

- **Architecture Guide:** `docs/ARCHITECTURE_GUIDE.md`
- **Notion Setup:** `docs/NOTION_SETUP.md`
- **Image Generator Code:** `src/image_generator.py`
- **Replicate Docs:** https://replicate.com/docs
- **Your Model:** https://replicate.com/sundai-club/pikachu_sfw

---

## ✨ Example Results

### Generated Image Files
```bash
$ ls -lh generated_images/
total 2.6M
-rw-r--r-- 1.3M  character_in_a_retail_store_analyzing_shelves_pro.png
-rw-r--r-- 1.3M  character_using_AI_tools_in_a_retail_store_setting.png
```

### Example Post
**Text:**
> As retail evolves, manual inventory tracking is becoming a burden. Leveraging existing cameras with AI not only cuts down labor but enhances accuracy and real-time insights. #RetailTech #InventoryManagement

**Image:** Custom Pikachu character using AI tools in a retail store setting

**Result:** Professional, branded social media post ready to engage your audience!

---

**Status:** ✅ Fully operational
**Last Updated:** January 21, 2026
**Branch:** `notion-integration`

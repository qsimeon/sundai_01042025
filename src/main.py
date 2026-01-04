#!/usr/bin/env python3
"""
InventoryVision AI - Social Media Automation
Main application that orchestrates post generation and engagement
"""

import os
import sys
from dotenv import load_dotenv
from post_generator import load_company_docs, generate_post, format_post_for_platform
from mastodon_client import MastodonClient
from reply_generator import generate_replies, display_reply_plan


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")


def main():
    """Main application flow"""
    print_header("InventoryVision AI - Social Media Automation")

    # Load environment variables
    load_dotenv()

    try:
        # 1. Load company documentation
        print("📚 Loading company documentation...")
        company_docs = load_company_docs()

        # 2. Connect to Mastodon
        print("\n🔗 Connecting to Mastodon...")
        mastodon = MastodonClient()

        # 3. Generate and post original content
        print_header("STEP 1: Generate Original Post")

        post_type = input("What type of post? (thought_leadership/product_update/industry_insight) [thought_leadership]: ").strip() or "thought_leadership"

        print(f"\n🤖 Generating {post_type} post...")
        post = generate_post(company_docs, post_type=post_type, platform="mastodon")

        print("\n" + "-"*70)
        print("GENERATED POST:")
        print("-"*70)
        formatted_post = format_post_for_platform(post)
        print(formatted_post)
        print("-"*70)

        should_post = input("\nPost this to Mastodon? (yes/no) [yes]: ").strip().lower()
        should_post = should_post if should_post else "yes"

        if should_post == "yes":
            print("\n📤 Posting to Mastodon...")
            status = mastodon.post(formatted_post)
            print(f"✓ Posted successfully: {status['url']}")
        else:
            print("\n⏭️  Skipped posting.")

        # 4. Find and engage with relevant posts
        print_header("STEP 2: Engage with Community")

        keywords = input("Search keyword for relevant posts [retail technology]: ").strip() or "retail technology"
        num_posts = input("How many posts to analyze? [5]: ").strip() or "5"

        try:
            num_posts = int(num_posts)
        except ValueError:
            num_posts = 5

        print(f"\n🔍 Searching for posts about '{keywords}'...")
        relevant_posts = mastodon.search_posts(keywords, limit=num_posts)

        if not relevant_posts:
            print(f"No posts found for '{keywords}'. Try a different keyword.")
            return

        print(f"✓ Found {len(relevant_posts)} posts")

        # 5. Generate replies using AI
        print(f"\n🤖 Analyzing posts and generating replies...")
        min_relevance = 6  # Only engage with highly relevant posts

        replies = generate_replies(company_docs, relevant_posts, min_relevance=min_relevance)

        if not replies:
            print(f"No posts met the relevance threshold ({min_relevance}/10).")
            return

        # Display reply plan
        display_reply_plan(replies)

        # 6. Post replies
        replies_to_post = [r for r in replies if r.should_reply]

        if not replies_to_post:
            print("\n No replies recommended by AI. All posts were either off-topic or")
            print("wouldn't benefit from our input.")
            return

        print(f"\n💬 {len(replies_to_post)} replies recommended")
        should_reply = input("\nPost these replies? (yes/no/review) [review]: ").strip().lower() or "review"

        if should_reply == "yes":
            print("\n📤 Posting replies...")
            for i, reply in enumerate(replies_to_post, 1):
                print(f"  [{i}/{len(replies_to_post)}] Replying to post {reply.post_id}...")
                mastodon.reply(reply.post_id, reply.reply_content)
            print("\n✓ All replies posted!")

        elif should_reply == "review":
            print("\n📝 Review each reply:")
            for i, reply in enumerate(replies_to_post, 1):
                print(f"\n--- Reply {i}/{len(replies_to_post)} ---")
                print(f"Post ID: {reply.post_id}")
                print(f"Relevance: {reply.relevance_score}/10")
                print(f"Reasoning: {reply.reasoning}")
                print(f"Reply: \"{reply.reply_content}\"")

                post_this = input("\nPost this reply? (yes/no) [yes]: ").strip().lower() or "yes"
                if post_this == "yes":
                    mastodon.reply(reply.post_id, reply.reply_content)
                    print("✓ Posted")
                else:
                    print("⏭️  Skipped")

        else:
            print("\n⏭️  Skipped reply posting.")

        print_header("✓ Automation Complete!")
        print("Your AI-powered social media presence is now active. 🚀")

    except ValueError as e:
        print(f"\n❌ Setup Error: {e}")
        print("\nPlease check your .env file and ensure all required credentials are set.")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⏸️  Interrupted by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Mastodon API Client
Wrapper for posting and searching on Mastodon
"""

from mastodon import Mastodon
import os
from typing import List, Dict, Any


class MastodonClient:
    """Client for interacting with Mastodon API"""

    def __init__(self):
        """Initialize Mastodon client with credentials from environment"""
        access_token = os.getenv('MASTODON_ACCESS_TOKEN')
        api_base_url = os.getenv('MASTODON_API_BASE_URL', 'https://mastodon.social')

        if not access_token:
            raise ValueError(
                "MASTODON_ACCESS_TOKEN not found in environment variables.\n"
                "Please create an application at: https://mastodon.social/settings/applications\n"
                "and add the access token to your .env file"
            )

        if access_token == "YOUR_MASTODON_ACCESS_TOKEN_HERE":
            raise ValueError(
                "Please update MASTODON_ACCESS_TOKEN in .env file with your actual token.\n"
                "Get it from: https://mastodon.social/settings/applications"
            )

        self.client = Mastodon(
            access_token=access_token,
            api_base_url=api_base_url
        )

        # Verify credentials
        try:
            account = self.client.me()
            print(f"✓ Connected to Mastodon as @{account['username']}")
        except Exception as e:
            raise ValueError(f"Failed to authenticate with Mastodon: {e}")

    def post(self, content: str, visibility: str = "public") -> Dict[str, Any]:
        """
        Post a status update (toot) to Mastodon

        Args:
            content: The text content to post
            visibility: Post visibility ('public', 'unlisted', 'private', 'direct')

        Returns:
            Dictionary containing the posted status information
        """
        try:
            status = self.client.status_post(
                content,
                visibility=visibility
            )
            print(f"✓ Posted to Mastodon: {status['url']}")
            return status
        except Exception as e:
            print(f"✗ Failed to post to Mastodon: {e}")
            raise

    def search_posts(
        self,
        query: str,
        limit: int = 5,
        resolve: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for posts containing a keyword

        Args:
            query: Search query string
            limit: Maximum number of results to return
            resolve: Whether to resolve remote accounts/statuses

        Returns:
            List of status dictionaries matching the search
        """
        try:
            results = self.client.search_v2(
                query,
                result_type="statuses",
                resolve=resolve
            )
            statuses = results.get('statuses', [])[:limit]
            print(f"✓ Found {len(statuses)} posts matching '{query}'")
            return statuses
        except Exception as e:
            print(f"✗ Failed to search Mastodon: {e}")
            raise

    def reply(
        self,
        post_id: str,
        content: str,
        visibility: str = "public"
    ) -> Dict[str, Any]:
        """
        Reply to an existing post

        Args:
            post_id: ID of the post to reply to
            content: Reply text content
            visibility: Reply visibility

        Returns:
            Dictionary containing the posted reply information
        """
        try:
            status = self.client.status_post(
                content,
                in_reply_to_id=post_id,
                visibility=visibility
            )
            print(f"✓ Replied to post {post_id}: {status['url']}")
            return status
        except Exception as e:
            print(f"✗ Failed to reply to post {post_id}: {e}")
            raise

    def get_account_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated account

        Returns:
            Dictionary containing account information
        """
        return self.client.me()

    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get a specific post by ID

        Args:
            post_id: ID of the post to retrieve

        Returns:
            Dictionary containing the post information
        """
        return self.client.status(post_id)


def format_post_info(post: Dict[str, Any]) -> str:
    """
    Format post information for display

    Args:
        post: Post dictionary from Mastodon API

    Returns:
        Formatted string with post information
    """
    account = post['account']['acct']
    content = post['content'].replace('<p>', '').replace('</p>', '\n').replace('<br />', '\n')
    # Remove HTML tags
    import re
    content = re.sub('<[^<]+?>', '', content).strip()

    created = post['created_at'].strftime("%Y-%m-%d %H:%M")

    return f"""
Post ID: {post['id']}
Author: @{account}
Created: {created}
URL: {post['url']}

Content:
{content}
"""


if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    load_dotenv()

    try:
        # Initialize client
        client = MastodonClient()

        # Get account info
        account = client.get_account_info()
        print(f"\nAccount: @{account['username']}")
        print(f"Display Name: {account['display_name']}")
        print(f"Followers: {account['followers_count']}")
        print(f"Following: {account['following_count']}")
        print(f"Posts: {account['statuses_count']}")

        # Example: Search for posts
        print("\n" + "="*60)
        print("Searching for posts about 'retail technology'...")
        print("="*60)
        posts = client.search_posts("retail technology", limit=3)

        for i, post in enumerate(posts, 1):
            print(f"\n--- Post {i} ---")
            print(format_post_info(post))

    except ValueError as e:
        print(f"\nSetup required: {e}")
    except Exception as e:
        print(f"\nError: {e}")

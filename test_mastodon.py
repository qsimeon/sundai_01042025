#!/usr/bin/env python3
"""
Test Mastodon token to verify it works
"""

import os
from dotenv import load_dotenv
from mastodon import Mastodon

load_dotenv(override=True)

token = os.getenv("MASTODON_ACCESS_TOKEN")
base_url = os.getenv("MASTODON_API_BASE_URL", "https://mastodon.social")

print("Testing Mastodon connection...")
print(f"Base URL: {base_url}")
print(f"Token: {token[:20]}..." if token else "Token: None")
print()

if not token:
    print("❌ No MASTODON_ACCESS_TOKEN found in .env")
    exit(1)

try:
    # Try to connect
    print("Connecting...")
    client = Mastodon(
        access_token=token,
        api_base_url=base_url
    )

    # Try to get account info
    print("Fetching account info...")
    account = client.me()

    print("\n✅ Success! Connection working.")
    print(f"Logged in as: @{account['username']}")
    print(f"Display name: {account['display_name']}")
    print(f"Account ID: {account['id']}")
    print(f"Followers: {account['followers_count']}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting steps:")
    print("1. Go to: https://mastodon.social/settings/applications")
    print("2. Click 'New Application'")
    print("3. Name: 'Inventory.AI Bot' (or anything)")
    print("4. Scopes: Make sure these are checked:")
    print("   ✓ read:accounts")
    print("   ✓ read:statuses")
    print("   ✓ write:statuses")
    print("5. Click 'Submit'")
    print("6. Copy 'Your access token' and paste it in .env as MASTODON_ACCESS_TOKEN")
    print("\n⚠️  Common issues:")
    print("   - Token has wrong scopes (needs read + write)")
    print("   - Token got revoked (create a new one)")
    print("   - Wrong base URL (should be https://mastodon.social)")

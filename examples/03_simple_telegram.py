#!/usr/bin/env python3
"""
Example 3: Simple Telegram Bot
Learn: How to send messages with Telegram Bot API

Run: uv run python examples/03_simple_telegram.py
"""

import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv

print("=" * 60)
print("EXAMPLE 3: Simple Telegram Bot")
print("=" * 60)

# Step 1: Load credentials
print("\n📁 Step 1: Loading Telegram credentials...")
load_dotenv(override=True)
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

if not token or not chat_id:
    print("❌ Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in .env")
    exit(1)

print(f"✓ Bot token: {token[:20]}...")
print(f"✓ Chat ID: {chat_id}")


async def send_test_message():
    """
    Async function to send a message.
    Note the 'async' keyword - this is an async function!
    """
    # Step 2: Create bot
    print("\n🤖 Step 2: Creating bot...")
    bot = Bot(token=token)
    print("✓ Bot created!")

    # Step 3: Get bot info
    print("\n📋 Step 3: Getting bot information...")
    me = await bot.get_me()  # Note the 'await' keyword!
    print(f"✓ Bot username: @{me.username}")
    print(f"✓ Bot name: {me.first_name}")

    # Step 4: Send a message
    print("\n📤 Step 4: Sending message to Telegram...")
    message = await bot.send_message(
        chat_id=chat_id,
        text="🎉 Hello from Python!\n\nThis is a test message from your bot. "
             "Check your Telegram app to see it!"
    )
    print("✓ Message sent!")
    print(f"✓ Message ID: {message.message_id}")

    print("\n📱 Check your Telegram app to see the message!")


# Step 5: Run the async function
print("\n⚡ Step 5: Running async function...")
print("(Note: asyncio.run() is needed to run async functions)")

try:
    asyncio.run(send_test_message())
    print("\n" + "=" * 60)
    print("✅ Example complete!")
    print("\n💡 Try changing the message on line 50-52")
    print("=" * 60)
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure:")
    print("1. Your bot token is correct")
    print("2. You've started a chat with your bot on Telegram")
    print("3. Your chat ID is correct")

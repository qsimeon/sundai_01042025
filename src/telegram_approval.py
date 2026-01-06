"""
Telegram Bot with Button-Based Approval
Sends posts to Telegram with approve/reject buttons and waits for user response.
"""

import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()


class TelegramApprovalBot:
    """Handles Telegram approval with buttons."""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))

        if not self.token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

        self.bot = Bot(token=self.token)
        self.approval_received = False
        self.user_approved = False

    async def send_approval_request(self, content: str, content_type: str = "post") -> bool:
        """
        Send approval request with buttons and wait for response.

        Args:
            content: The post/reply content
            content_type: "post" or "reply"

        Returns:
            True if approved, False if rejected
        """
        icon = "📝" if content_type == "post" else "💬"

        # Escape markdown special characters in content for display
        # Don't parse content as markdown to avoid issues
        message_text = f"{icon} Approval Request: {content_type.upper()}\n\n"
        message_text += f"Content:\n{content}\n\n"
        message_text += f"Character count: {len(content)}/500\n\n"
        message_text += f"Approve this {content_type}?"

        # Create buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data="approve"),
                InlineKeyboardButton("❌ Reject", callback_data="reject"),
            ]
        ])

        # Send message (no markdown parsing to avoid errors)
        message = await self.bot.send_message(
            chat_id=self.chat_id,
            text=message_text,
            reply_markup=keyboard
        )

        print(f"📱 Approval request sent to Telegram!")
        print(f"⏳ Waiting for you to press a button in Telegram...")
        print(f"   (Check your phone/Telegram app)")

        # Set up the application to listen for button presses
        app = Application.builder().token(self.token).build()

        # Add callback handler
        app.add_handler(CallbackQueryHandler(self._handle_button))

        # Initialize and start
        await app.initialize()
        await app.start()

        # Wait for response (timeout after 5 minutes)
        timeout = 300  # 5 minutes
        elapsed = 0

        while not self.approval_received and elapsed < timeout:
            # Get updates
            try:
                updates = await app.bot.get_updates(offset=None, timeout=1)

                # Process each update
                for update in updates:
                    await app.process_update(update)

                    # Check if we got the response
                    if self.approval_received:
                        break

                if self.approval_received:
                    break

            except Exception as e:
                # Ignore timeout errors
                pass

            await asyncio.sleep(1)
            elapsed += 1

        # Cleanup
        await app.stop()
        await app.shutdown()

        # Check result
        if not self.approval_received:
            print("⏱️ Timeout - no response received after 5 minutes")
            return False

        if self.user_approved:
            print("✅ Approved by user!")
            return True
        else:
            print("❌ Rejected by user")
            return False

    async def _handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button press from user."""
        query = update.callback_query
        await query.answer()  # Acknowledge button press

        # Get the response
        response = query.data

        # Mark as received
        self.approval_received = True
        self.user_approved = (response == "approve")

        # Update the message
        if response == "approve":
            await query.edit_message_text(
                "✅ APPROVED\n\nPosting to Mastodon..."
            )
        else:
            await query.edit_message_text(
                "❌ REJECTED\n\nPost cancelled."
            )

    async def send_notification(self, message: str):
        """Send a simple notification (no markdown parsing)."""
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message
        )


def request_approval(content: str, content_type: str = "post") -> bool:
    """
    Request approval with Telegram buttons (synchronous wrapper).

    Args:
        content: The content to approve
        content_type: "post" or "reply"

    Returns:
        True if approved, False if rejected
    """
    bot = TelegramApprovalBot()
    return asyncio.run(bot.send_approval_request(content, content_type))


def send_notification(message: str):
    """Send notification to Telegram (synchronous wrapper)."""
    bot = TelegramApprovalBot()
    asyncio.run(bot.send_notification(message))


if __name__ == "__main__":
    # Test the approval workflow
    print("🧪 Testing Telegram approval workflow...")

    test_content = """Transform retail inventory with AI! Our VLM + SAM3D solution uses security cameras for smart tracking. #RetailTech #AI"""

    approved = request_approval(test_content, "post")

    if approved:
        send_notification("✅ Test successful! Approval workflow is working correctly.")
    else:
        send_notification("❌ Test completed - post was rejected.")

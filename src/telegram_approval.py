"""
Telegram Bot with Button-Based Approval and Rejection Feedback
Sends posts to Telegram with approve/reject buttons, waits for user response,
and captures rejection reasons when posts are rejected.
"""

import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv(override=True)


class TelegramApprovalBot:
    """Handles Telegram approval with buttons and rejection feedback."""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))

        if not self.token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

        self.bot = Bot(token=self.token)
        self.approval_received = False
        self.user_approved = False
        self.current_message_id = None
        self.rejection_reason = None
        self.waiting_for_feedback = False
        self.content_for_logging = None

    async def send_approval_request(
        self,
        content: str,
        content_type: str = "post",
        image_path: str = None
    ) -> tuple[bool, str | None]:
        """
        Send approval request with buttons and wait for response.
        If rejected, asks for and captures the reason.

        Args:
            content: The post/reply content
            content_type: "post" or "reply"
            image_path: Optional path to image to preview

        Returns:
            Tuple of (approved: bool, rejection_reason: str | None)
        """
        # Reset state
        self.approval_received = False
        self.user_approved = False
        self.rejection_reason = None
        self.waiting_for_feedback = False
        self.content_for_logging = content

        icon = "📝" if content_type == "post" else "💬"

        # Build caption/message text
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

        # Send message with or without image
        if image_path:
            with open(image_path, 'rb') as photo:
                message = await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=photo,
                    caption=message_text,
                    reply_markup=keyboard
                )
        else:
            message = await self.bot.send_message(
                chat_id=self.chat_id,
                text=message_text,
                reply_markup=keyboard
            )

        self.current_message_id = message.message_id

        print(f"📱 Approval request sent to Telegram!")
        print(f"⏳ Waiting for you to press a button in Telegram...")
        print(f"   (Check your phone/Telegram app)")

        # Set up the application
        app = Application.builder().token(self.token).build()

        # Add handlers
        app.add_handler(CallbackQueryHandler(self._handle_button))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text))

        # Initialize and start
        await app.initialize()
        await app.start()

        # Wait for response (timeout after 5 minutes)
        timeout = 300  # 5 minutes
        elapsed = 0

        while not self.approval_received and elapsed < timeout:
            try:
                updates = await app.bot.get_updates(offset=None, timeout=1)

                for update in updates:
                    await app.process_update(update)

                    if self.approval_received:
                        break

                if self.approval_received:
                    break

            except Exception:
                pass

            await asyncio.sleep(1)
            elapsed += 1

        # Cleanup
        await app.stop()
        await app.shutdown()

        # Check result
        if not self.approval_received:
            print("⏱️ Timeout - no response received after 5 minutes")
            return False, None

        if self.user_approved:
            print("✅ Approved by user!")
            return True, None
        else:
            print(f"❌ Rejected by user")
            if self.rejection_reason:
                print(f"   Reason: {self.rejection_reason}")
                # Log the rejection
                self._log_rejection(content, content_type, self.rejection_reason)
            return False, self.rejection_reason

    async def _handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button press from user."""
        query = update.callback_query

        # Only handle callbacks for the message we're currently waiting for
        if query.message.message_id != self.current_message_id:
            try:
                await query.answer()
            except Exception:
                pass
            return

        await query.answer()
        response = query.data

        if response == "approve":
            self.approval_received = True
            self.user_approved = True

            try:
                await query.edit_message_text("✅ APPROVED\n\nPosting to Mastodon...")
            except Exception:
                pass

        elif response == "reject":
            # Don't mark as fully received yet - we need the reason
            self.user_approved = False
            self.waiting_for_feedback = True

            try:
                await query.edit_message_text(
                    "❌ REJECTED\n\n"
                    "Please reply with the reason for rejection.\n"
                    "This feedback helps improve future posts.\n\n"
                    "Examples:\n"
                    "• 'Too promotional'\n"
                    "• 'Wrong tone'\n"
                    "• 'Factually incorrect'\n"
                    "• 'Not relevant to our brand'"
                )
            except Exception:
                pass

    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (for rejection feedback)."""
        if not self.waiting_for_feedback:
            return

        self.rejection_reason = update.message.text
        self.waiting_for_feedback = False
        self.approval_received = True  # Now we're done

        await update.message.reply_text(
            f"📝 Feedback recorded!\n\n"
            f"Reason: {self.rejection_reason}\n\n"
            f"This will help improve future posts. Thank you!"
        )

    def _log_rejection(self, content: str, content_type: str, reason: str):
        """Log rejection feedback to a JSON file."""
        log_file = Path("feedback_log.json")

        # Load existing log
        if log_file.exists():
            with open(log_file, 'r') as f:
                try:
                    log = json.load(f)
                except json.JSONDecodeError:
                    log = []
        else:
            log = []

        # Add new entry
        log.append({
            "timestamp": datetime.now().isoformat(),
            "content_type": content_type,
            "content": content[:200],  # First 200 chars
            "rejection_reason": reason
        })

        # Save log
        with open(log_file, 'w') as f:
            json.dump(log, f, indent=2)

        print(f"   💾 Logged to feedback_log.json")

    async def send_notification(self, message: str):
        """Send a simple notification (no markdown parsing)."""
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message
        )


def request_approval(
    content: str,
    content_type: str = "post",
    image_path: str = None
) -> tuple[bool, str | None]:
    """
    Request approval with Telegram buttons (synchronous wrapper).
    If rejected, captures the reason.

    Args:
        content: The content to approve
        content_type: "post" or "reply"
        image_path: Optional path to image to preview

    Returns:
        Tuple of (approved: bool, rejection_reason: str | None)
    """
    bot = TelegramApprovalBot()
    return asyncio.run(bot.send_approval_request(content, content_type, image_path))


def send_notification(message: str):
    """Send notification to Telegram (synchronous wrapper)."""
    bot = TelegramApprovalBot()
    asyncio.run(bot.send_notification(message))


if __name__ == "__main__":
    # Test the approval workflow with feedback
    print("🧪 Testing Telegram approval workflow with rejection feedback...")

    test_content = """Transform retail inventory with AI! Our VLM + SAM3D solution uses security cameras for smart tracking. #RetailTech #AI"""

    approved, reason = request_approval(test_content, "post")

    if approved:
        send_notification("✅ Test successful! Approval workflow is working correctly.")
    else:
        if reason:
            send_notification(f"❌ Test completed - post was rejected.\n\nReason: {reason}")
        else:
            send_notification("❌ Test completed - post was rejected (no reason provided).")

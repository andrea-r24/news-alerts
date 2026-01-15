"""
Telegram notification module.
Sends digest messages to Telegram with formatted article lists.
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Dict
import pytz

from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends notifications via Telegram bot."""

    def __init__(self, bot_token: str, chat_id: str, timezone: str = "America/Lima"):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token from BotFather
            chat_id: Chat ID to send messages to
            timezone: Timezone for timestamps in messages
        """
        if not bot_token or not chat_id:
            logger.warning("Telegram credentials not provided, notifications will be skipped")
            self.bot = None
            self.chat_id = None
        else:
            self.bot = Bot(token=bot_token)
            self.chat_id = chat_id

        self.timezone = pytz.timezone(timezone)

    def format_digest_message(self, articles: List[Dict], max_articles: int = 5) -> str:
        """
        Format articles as a digest message.

        Args:
            articles: List of article dictionaries (should be sorted by date, newest first)
            max_articles: Maximum number of articles to include

        Returns:
            Formatted message string
        """
        # Get current time in specified timezone
        now = datetime.now(self.timezone)
        time_str = now.strftime("%I:%M %p")  # e.g., "08:00 AM"

        # Build message header
        message_parts = [
            f"🗞️ <b>AI News Digest - {time_str}</b>\n"
        ]

        # Add articles (limit to max_articles)
        articles_to_show = articles[:max_articles]

        for idx, article in enumerate(articles_to_show, 1):
            title = article.get('title', 'Untitled')
            url = article.get('url', '')

            # Escape HTML special characters in title
            title = self._escape_html(title)

            message_parts.append(f"{idx}. {title}")
            message_parts.append(f"   → {url}\n")

        # Join all parts
        message = "\n".join(message_parts)

        return message

    def _escape_html(self, text: str) -> str:
        """
        Escape HTML special characters for Telegram HTML formatting.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))

    async def _send_message_async(self, message: str, retry_count: int = 3) -> bool:
        """
        Send message asynchronously with retry logic.

        Args:
            message: Message text to send
            retry_count: Number of retries on failure

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.bot or not self.chat_id:
            logger.warning("Telegram bot not configured, skipping message send")
            return False

        for attempt in range(retry_count):
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                logger.info("Successfully sent Telegram notification")
                return True

            except TelegramError as e:
                logger.warning(f"Telegram error on attempt {attempt + 1}/{retry_count}: {e}")

                if attempt < retry_count - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to send Telegram notification after {retry_count} attempts")
                    return False

            except Exception as e:
                logger.error(f"Unexpected error sending Telegram message: {e}")
                return False

        return False

    def send_digest(self, articles: List[Dict], max_articles: int = 5) -> bool:
        """
        Send digest notification with top articles.

        Args:
            articles: List of article dictionaries (will be limited to max_articles)
            max_articles: Maximum number of articles to include

        Returns:
            True if sent successfully, False otherwise
        """
        if not articles:
            logger.info("No articles to send, skipping notification")
            return False

        # Format the digest message
        message = self.format_digest_message(articles, max_articles)

        # Send the message
        try:
            # Run async function in event loop
            return asyncio.run(self._send_message_async(message))
        except Exception as e:
            logger.error(f"Error in send_digest: {e}")
            return False

    def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification (optional, for critical failures).

        Args:
            error_message: Error message to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.bot or not self.chat_id:
            return False

        message = f"⚠️ <b>AI News Alerts Error</b>\n\n{self._escape_html(error_message)}"

        try:
            return asyncio.run(self._send_message_async(message, retry_count=1))
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False

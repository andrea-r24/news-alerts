"""
AI News Alerts - Main Entry Point

Fetches news from multiple sources, filters by keywords, and sends
Telegram digest notifications.
"""

import logging
import sys
from datetime import datetime

from src.config import (
    KEYWORDS,
    RSS_FEEDS,
    NEWSAPI_KEY,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TIMEZONE,
    STORAGE_PATH,
    RSS_FETCH_TIMEOUT,
    FETCH_WINDOW_HOURS,
    MAX_ARTICLES_IN_DIGEST,
    CLEANUP_DAYS
)
from src.news_fetcher import NewsFetcher
from src.keyword_matcher import KeywordMatcher
from src.telegram_notifier import TelegramNotifier
from src.storage import ArticleStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main execution flow."""
    try:
        logger.info("=" * 60)
        logger.info("Starting AI News Alerts check...")
        logger.info(f"Time: {datetime.now()}")
        logger.info("=" * 60)

        # 1. Initialize components
        logger.info("Initializing components...")
        storage = ArticleStorage(STORAGE_PATH)
        fetcher = NewsFetcher(RSS_FEEDS, NEWSAPI_KEY, timeout=RSS_FETCH_TIMEOUT)
        matcher = KeywordMatcher(KEYWORDS)
        notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TIMEZONE)

        # Log storage stats
        stats = storage.get_stats()
        logger.info(f"Storage stats: {stats['total']} articles tracked")

        # 2. Fetch articles from all sources
        logger.info(f"Fetching articles from the last {FETCH_WINDOW_HOURS} hours...")
        all_articles = fetcher.fetch_all_articles(KEYWORDS, hours_ago=FETCH_WINDOW_HOURS)
        logger.info(f"Fetched {len(all_articles)} total articles")

        if not all_articles:
            logger.info("No articles found from any source")
            return

        # 3. Filter by keywords
        logger.info("Filtering articles by keywords...")
        matched_articles = matcher.filter_articles(all_articles)
        logger.info(f"Found {len(matched_articles)} articles matching keywords")

        if not matched_articles:
            logger.info("No articles matched the configured keywords")
            return

        # Log keyword statistics
        keyword_stats = matcher.get_keyword_stats(matched_articles)
        logger.info(f"Keyword match stats: {keyword_stats}")

        # 4. Filter out already sent articles
        logger.info("Checking for new articles (filtering out already sent)...")
        new_articles = [
            article for article in matched_articles
            if not storage.is_sent(article['url'])
        ]
        logger.info(f"Found {len(new_articles)} new articles (not previously sent)")

        if not new_articles:
            logger.info("No new articles to send - all matching articles were already sent")
            return

        # 5. Sort by publication date (newest first)
        new_articles.sort(key=lambda x: x['published'], reverse=True)

        # 6. Take top N articles for digest
        articles_to_send = new_articles[:MAX_ARTICLES_IN_DIGEST]
        logger.info(f"Preparing digest with top {len(articles_to_send)} articles")

        # Log article details
        for idx, article in enumerate(articles_to_send, 1):
            logger.info(f"  {idx}. {article['title'][:80]}... ({article['source']})")

        # 7. Send digest notification
        logger.info("Sending Telegram digest...")
        success = notifier.send_digest(articles_to_send, max_articles=MAX_ARTICLES_IN_DIGEST)

        if success:
            # 8. Mark articles as sent
            logger.info("Marking articles as sent...")
            storage.mark_multiple_as_sent(articles_to_send)
            logger.info(f"Successfully sent and tracked {len(articles_to_send)} articles")
        else:
            logger.error("Failed to send Telegram notification - articles NOT marked as sent")

        # 9. Cleanup old entries
        logger.info(f"Cleaning up entries older than {CLEANUP_DAYS} days...")
        removed = storage.cleanup_old_entries(days=CLEANUP_DAYS)
        if removed > 0:
            logger.info(f"Removed {removed} old entries")

        logger.info("=" * 60)
        logger.info("AI News Alerts check completed successfully")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)

        # Optionally send error notification to Telegram
        try:
            notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TIMEZONE)
            notifier.send_error_notification(f"Critical error: {str(e)}")
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()

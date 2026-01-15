"""
Storage module for tracking sent articles.
Uses JSON file to persist article data between runs.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ArticleStorage:
    """Manages storage of sent articles to prevent duplicates."""

    def __init__(self, storage_path: str):
        """
        Initialize storage with path to JSON file.

        Args:
            storage_path: Path to the JSON storage file
        """
        self.storage_path = Path(storage_path)
        self.ensure_storage_exists()

    def ensure_storage_exists(self) -> None:
        """Create storage file and directory if they don't exist."""
        # Create parent directory if needed
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize with empty dict if file doesn't exist
        if not self.storage_path.exists():
            self.save_sent_articles({})
            logger.info(f"Created new storage file at {self.storage_path}")

    def load_sent_articles(self) -> Dict:
        """
        Load sent articles from JSON file.

        Returns:
            Dictionary mapping article URLs to metadata
            Format: {
                'article_url': {
                    'sent_at': 'ISO datetime',
                    'title': 'article title',
                    'url': 'article url'
                }
            }
        """
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {self.storage_path}, returning empty dict")
            return {}
        except Exception as e:
            logger.error(f"Error loading sent articles: {e}")
            return {}

    def save_sent_articles(self, data: Dict) -> None:
        """
        Save sent articles to JSON file.

        Args:
            data: Dictionary of sent articles
        """
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(data)} articles to storage")
        except Exception as e:
            logger.error(f"Error saving sent articles: {e}")
            raise

    def is_sent(self, article_url: str) -> bool:
        """
        Check if an article URL has already been sent.

        Args:
            article_url: URL of the article to check

        Returns:
            True if article was already sent, False otherwise
        """
        sent_articles = self.load_sent_articles()
        return article_url in sent_articles

    def mark_as_sent(self, article: Dict) -> None:
        """
        Mark an article as sent with current timestamp.

        Args:
            article: Article dictionary with at least 'url' and 'title' keys
        """
        sent_articles = self.load_sent_articles()

        article_url = article.get('url', '')
        if not article_url:
            logger.warning("Cannot mark article as sent: missing URL")
            return

        sent_articles[article_url] = {
            'sent_at': datetime.now().isoformat(),
            'title': article.get('title', ''),
            'url': article_url
        }

        self.save_sent_articles(sent_articles)
        logger.debug(f"Marked article as sent: {article.get('title', 'Untitled')}")

    def mark_multiple_as_sent(self, articles: list) -> None:
        """
        Mark multiple articles as sent in a single operation.

        Args:
            articles: List of article dictionaries
        """
        sent_articles = self.load_sent_articles()
        current_time = datetime.now().isoformat()

        for article in articles:
            article_url = article.get('url', '')
            if article_url:
                sent_articles[article_url] = {
                    'sent_at': current_time,
                    'title': article.get('title', ''),
                    'url': article_url
                }

        self.save_sent_articles(sent_articles)
        logger.info(f"Marked {len(articles)} articles as sent")

    def cleanup_old_entries(self, days: int = 30) -> int:
        """
        Remove entries older than specified days to keep file manageable.

        Args:
            days: Number of days to keep (entries older than this will be removed)

        Returns:
            Number of entries removed
        """
        sent_articles = self.load_sent_articles()
        cutoff_date = datetime.now() - timedelta(days=days)

        # Filter out old entries
        original_count = len(sent_articles)
        sent_articles = {
            url: data
            for url, data in sent_articles.items()
            if datetime.fromisoformat(data['sent_at']) > cutoff_date
        }

        removed_count = original_count - len(sent_articles)

        if removed_count > 0:
            self.save_sent_articles(sent_articles)
            logger.info(f"Cleaned up {removed_count} old entries (older than {days} days)")

        return removed_count

    def get_stats(self) -> Dict:
        """
        Get statistics about stored articles.

        Returns:
            Dictionary with stats (total count, oldest/newest dates)
        """
        sent_articles = self.load_sent_articles()

        if not sent_articles:
            return {
                'total': 0,
                'oldest': None,
                'newest': None
            }

        dates = [datetime.fromisoformat(data['sent_at']) for data in sent_articles.values()]

        return {
            'total': len(sent_articles),
            'oldest': min(dates).isoformat(),
            'newest': max(dates).isoformat()
        }

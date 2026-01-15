"""
News fetching module for RSS feeds and NewsAPI.
Handles fetching, parsing, and normalizing articles from multiple sources.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz

import feedparser
import requests
from newsapi import NewsApiClient
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class RSSFetcher:
    """Fetches and parses RSS feeds."""

    def __init__(self, timeout: int = 10):
        """
        Initialize RSS fetcher.

        Args:
            timeout: Timeout in seconds for feed requests
        """
        self.timeout = timeout

    def fetch_feed(self, feed_url: str, source_name: str, hours_ago: int = 8) -> List[Dict]:
        """
        Fetch RSS feed and return articles from last N hours.

        Args:
            feed_url: URL of the RSS feed
            source_name: Name of the source (for article metadata)
            hours_ago: Number of hours to look back

        Returns:
            List of normalized article dictionaries
        """
        articles = []

        try:
            logger.info(f"Fetching RSS feed: {source_name}")

            # Parse the feed
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                logger.warning(f"Feed {source_name} may be malformed: {feed.bozo_exception}")

            # Calculate cutoff time
            cutoff_time = datetime.now(pytz.UTC) - timedelta(hours=hours_ago)

            # Process entries
            for entry in feed.entries:
                try:
                    article = self._normalize_entry(entry, source_name)

                    # Filter by publication date
                    if article and article['published'] >= cutoff_time:
                        articles.append(article)

                except Exception as e:
                    logger.warning(f"Error processing RSS entry: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} recent articles from {source_name}")

        except requests.Timeout:
            logger.warning(f"Timeout fetching RSS feed: {source_name}")
        except Exception as e:
            logger.error(f"Error fetching RSS feed {source_name}: {e}")

        return articles

    def _normalize_entry(self, entry, source_name: str) -> Optional[Dict]:
        """
        Normalize RSS entry to standard article format.

        Args:
            entry: RSS feed entry
            source_name: Name of the source

        Returns:
            Normalized article dictionary or None if invalid
        """
        # Extract URL
        url = entry.get('link', '')
        if not url:
            return None

        # Extract title
        title = entry.get('title', 'Untitled')

        # Extract description/summary
        description = entry.get('summary', '') or entry.get('description', '')
        # Strip HTML tags from description if present
        if description:
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()

        # Parse publication date
        published = None
        pub_date_str = entry.get('published', '') or entry.get('updated', '')

        if pub_date_str:
            try:
                published = date_parser.parse(pub_date_str)
                # Ensure timezone aware
                if published.tzinfo is None:
                    published = pytz.UTC.localize(published)
            except Exception as e:
                logger.debug(f"Could not parse date '{pub_date_str}': {e}")

        # Default to current time if no date found
        if not published:
            published = datetime.now(pytz.UTC)

        return {
            'url': url,
            'title': title,
            'description': description,
            'published': published,
            'source': source_name
        }


class NewsAPIFetcher:
    """Fetches articles from NewsAPI."""

    def __init__(self, api_key: str):
        """
        Initialize NewsAPI fetcher.

        Args:
            api_key: NewsAPI key
        """
        if not api_key:
            logger.warning("NewsAPI key not provided, NewsAPI fetching will be skipped")
            self.client = None
        else:
            self.client = NewsApiClient(api_key=api_key)

    def fetch_articles(self, keywords: List[str], hours_ago: int = 8) -> List[Dict]:
        """
        Query NewsAPI with keywords from last N hours.

        Args:
            keywords: List of keywords to search for
            hours_ago: Number of hours to look back

        Returns:
            List of normalized article dictionaries
        """
        articles = []

        if not self.client:
            logger.info("NewsAPI client not initialized, skipping NewsAPI fetch")
            return articles

        try:
            logger.info("Fetching articles from NewsAPI")

            # Build query string: combine keywords with OR
            query = ' OR '.join(f'"{kw}"' for kw in keywords)

            # Calculate date range
            from_date = datetime.now() - timedelta(hours=hours_ago)

            # Query NewsAPI (using everything endpoint for free tier)
            response = self.client.get_everything(
                q=query,
                from_param=from_date.isoformat(),
                language='en',
                sort_by='publishedAt',
                page_size=100  # Maximum for free tier
            )

            # Process articles
            if response['status'] == 'ok':
                for article_data in response['articles']:
                    try:
                        article = self._normalize_article(article_data)
                        if article:
                            articles.append(article)
                    except Exception as e:
                        logger.warning(f"Error processing NewsAPI article: {e}")
                        continue

                logger.info(f"Fetched {len(articles)} articles from NewsAPI")
            else:
                logger.warning(f"NewsAPI response status: {response['status']}")

        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")

        return articles

    def _normalize_article(self, article_data: Dict) -> Optional[Dict]:
        """
        Normalize NewsAPI article to standard format.

        Args:
            article_data: Article data from NewsAPI

        Returns:
            Normalized article dictionary or None if invalid
        """
        # Extract URL
        url = article_data.get('url', '')
        if not url:
            return None

        # Extract title
        title = article_data.get('title', 'Untitled')

        # Extract description
        description = article_data.get('description', '') or article_data.get('content', '')

        # Parse publication date
        published = None
        pub_date_str = article_data.get('publishedAt', '')

        if pub_date_str:
            try:
                published = date_parser.parse(pub_date_str)
                # Ensure timezone aware
                if published.tzinfo is None:
                    published = pytz.UTC.localize(published)
            except Exception as e:
                logger.debug(f"Could not parse date '{pub_date_str}': {e}")

        # Default to current time if no date found
        if not published:
            published = datetime.now(pytz.UTC)

        # Extract source name
        source_name = article_data.get('source', {}).get('name', 'NewsAPI')

        return {
            'url': url,
            'title': title,
            'description': description,
            'published': published,
            'source': source_name
        }


class NewsFetcher:
    """Orchestrates fetching from all news sources."""

    def __init__(self, rss_feeds: Dict[str, str], newsapi_key: str, timeout: int = 10):
        """
        Initialize news fetcher with all sources.

        Args:
            rss_feeds: Dictionary mapping source names to RSS feed URLs
            newsapi_key: NewsAPI key
            timeout: Timeout for RSS requests
        """
        self.rss_fetcher = RSSFetcher(timeout=timeout)
        self.newsapi_fetcher = NewsAPIFetcher(api_key=newsapi_key)
        self.rss_feeds = rss_feeds

    def fetch_all_articles(self, keywords: List[str], hours_ago: int = 8) -> List[Dict]:
        """
        Fetch articles from all sources and combine.

        Args:
            keywords: Keywords to search for (used by NewsAPI)
            hours_ago: Number of hours to look back

        Returns:
            Combined and deduplicated list of articles
        """
        all_articles = []

        # Fetch from all RSS feeds
        for source_name, feed_url in self.rss_feeds.items():
            articles = self.rss_fetcher.fetch_feed(feed_url, source_name, hours_ago)
            all_articles.extend(articles)

        # Fetch from NewsAPI
        newsapi_articles = self.newsapi_fetcher.fetch_articles(keywords, hours_ago)
        all_articles.extend(newsapi_articles)

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []

        for article in all_articles:
            url = article['url']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)

        logger.info(f"Total articles fetched: {len(unique_articles)} (deduplicated from {len(all_articles)})")

        return unique_articles

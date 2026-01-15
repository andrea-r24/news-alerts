"""
Keyword matching module for filtering articles.
Uses regex with word boundaries for accurate matching.
"""

import re
import logging
from typing import List, Dict, Set

logger = logging.getLogger(__name__)


class KeywordMatcher:
    """Matches articles against configured keywords."""

    def __init__(self, keywords: List[str]):
        """
        Initialize matcher with keywords.

        Args:
            keywords: List of keywords to match against
        """
        self.keywords = keywords

        # Compile regex patterns for efficient matching
        # Use word boundaries to avoid partial matches
        # Case-insensitive matching
        self.patterns = [
            re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
            for kw in keywords
        ]

        logger.info(f"Initialized keyword matcher with {len(keywords)} keywords")

    def find_matches(self, article: Dict) -> Set[str]:
        """
        Find all matching keywords in article title and description.

        Args:
            article: Article dictionary with 'title' and 'description' keys

        Returns:
            Set of matched keywords (preserves original case from keywords list)
        """
        # Combine title and description for searching
        title = article.get('title', '')
        description = article.get('description', '')
        text = f"{title} {description}"

        matched_keywords = set()

        # Check each pattern against the text
        for pattern, keyword in zip(self.patterns, self.keywords):
            if pattern.search(text):
                matched_keywords.add(keyword)

        return matched_keywords

    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter articles that match any keyword.
        Enriches each article with 'matched_keywords' field.

        Args:
            articles: List of article dictionaries

        Returns:
            List of articles that match at least one keyword,
            with 'matched_keywords' field added
        """
        filtered_articles = []

        for article in articles:
            matched_keywords = self.find_matches(article)

            if matched_keywords:
                # Add matched keywords to article
                article['matched_keywords'] = list(matched_keywords)
                filtered_articles.append(article)

        logger.info(f"Filtered {len(filtered_articles)} matching articles from {len(articles)} total")

        return filtered_articles

    def get_keyword_stats(self, articles: List[Dict]) -> Dict[str, int]:
        """
        Get statistics on keyword matches across articles.

        Args:
            articles: List of filtered articles (with 'matched_keywords' field)

        Returns:
            Dictionary mapping keywords to match counts
        """
        stats = {kw: 0 for kw in self.keywords}

        for article in articles:
            matched_keywords = article.get('matched_keywords', [])
            for kw in matched_keywords:
                if kw in stats:
                    stats[kw] += 1

        return stats

"""
Configuration module for AI News Alerts system.
Centralizes all settings, keywords, RSS feeds, and environment variables.
"""

import os
from typing import List, Dict

# Keywords to monitor in articles
KEYWORDS: List[str] = [
    "OpenAI",
    "Anthropic",
    "Gemini AI",
    "AI agents",
    "agentic AI",
    "agentic commerce",
    "agentic payments",
    "financial agents",
    "agent protocol",
    "agent SDK"
]

# RSS Feed URLs to monitor
RSS_FEEDS: Dict[str, str] = {
    "VentureBeat": "https://venturebeat.com/feed/",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index"
}

# Environment variables for API keys and credentials
NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

# Timezone configuration (Lima, Peru is UTC-5)
TIMEZONE: str = "America/Lima"

# Storage configuration
STORAGE_PATH: str = "data/sent_articles.json"

# API Rate Limits
NEWSAPI_MAX_REQUESTS: int = 100  # Free tier daily limit
RSS_FETCH_TIMEOUT: int = 10  # seconds

# Fetch window (hours to look back for articles)
FETCH_WINDOW_HOURS: int = 8

# Digest configuration
MAX_ARTICLES_IN_DIGEST: int = 5

# Cleanup configuration (days to keep sent articles in storage)
CLEANUP_DAYS: int = 30

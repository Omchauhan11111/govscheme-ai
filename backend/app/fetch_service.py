import feedparser
import requests
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
import logging

from datetime import datetime, timedelta

from .config import settings
from .database import get_db

logger = logging.getLogger(__name__)

def fetch_all_feeds() -> dict:
    """Fetch schemes from all RSS feeds"""
    db = get_db()
    total_fetched = 0
    total_new = 0
    errors = []

    for feed_url in settings.RSS_FEEDS:
        try:
            result = _fetch_single_feed(feed_url, db)
            total_fetched += result["fetched"]
            total_new += result["new"]
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Error fetching {feed_url}: {e}")

    return {
        "total_fetched": total_fetched,
        "total_new": total_new,
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat()
    }

def _fetch_single_feed(feed_url: str, db) -> dict:
    feed = feedparser.parse(feed_url)
    fetched = 0
    new_count = 0
    cutoff = datetime.utcnow() - timedelta(days=7)  # 7 din se purani skip

    for entry in feed.entries:
        fetched += 1
        try:
            scheme_doc = _parse_entry(entry)
            
            # 7 din se purani news skip karo
            if scheme_doc["published_date"] < cutoff:
                continue
                
            # Duplicate check
            existing = db.schemes.find_one({"url": scheme_doc["url"]})
            if not existing:
                db.schemes.insert_one(scheme_doc)
                new_count += 1
        except Exception as e:
            logger.warning(f"Skipped entry: {e}")

    return {"fetched": fetched, "new": new_count}

def _parse_entry(entry) -> dict:
    """Parse RSS entry into scheme document"""
    # Clean summary from HTML tags
    raw_summary = getattr(entry, 'summary', '') or ''
    soup = BeautifulSoup(raw_summary, 'html.parser')
    clean_summary = soup.get_text(separator=' ').strip()

    # Parse date
    published = datetime.utcnow()
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            published = datetime(*entry.published_parsed[:6])
        except:
            pass

    url = getattr(entry, 'link', '') or getattr(entry, 'id', '')

    return {
        "title": getattr(entry, 'title', 'Untitled'),
        "url": url,
        "summary": clean_summary[:1000],
        "source": getattr(entry, 'source', {}).get('title', 'Unknown') if hasattr(entry, 'source') else 'Google News',
        "published_date": published,
        "fetched_at": datetime.utcnow(),
        "is_relevant": None,         # Will be set by AI filter
        "category": None,            # Will be set by AI filter
        "ai_summary": None,          # Will be set by AI filter
        "blog_generated": False,
        "blog_id": None,
        "wp_post_id": None,
        "status": "fetched"
    }

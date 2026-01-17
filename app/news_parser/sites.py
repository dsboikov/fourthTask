import feedparser
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class NewsParser:
    def __init__(self):
        self.sources = {
            "habr.com": "https://habr.com/ru/rss/articles/?fl=ru",
            "tproger.ru": "https://tproger.ru/feed/",
            "vc.ru": "https://vc.ru/rss"
        }

    def parse_all(self) -> List[Dict]:
        all_news = []
        for source, url in self.sources.items():
            try:
                news = self._parse_feed(source, url)
                all_news.extend(news)
                logger.info(f"Fetched {len(news)} items from {source}")
            except Exception as e:
                logger.error(f"Failed to parse {source}: {e}")
        return all_news

    @staticmethod
    def _parse_feed(source: str, feed_url: str) -> List[Dict]:
        feed = feedparser.parse(feed_url)
        items = []
        for entry in feed.entries:
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            else:
                published_at = datetime.now()

            items.append({
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "source": source,
                "published_at": published_at
            })
        return items

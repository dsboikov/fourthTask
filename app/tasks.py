from celery_worker import celery_app
from app.news_parser.sites import NewsParser
from app.database import SessionLocal
from app.models import NewsItem
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def fetch_news_from_sites():
    parser = NewsParser()
    news_items = parser.parse_all()

    db = SessionLocal()
    added = 0
    try:
        for item in news_items:
            # Проверяем, существует ли запись по URL
            existing = db.query(NewsItem).filter(NewsItem.url == item["url"]).first()
            if not existing:
                db_item = NewsItem(**item)
                db.add(db_item)
                added += 1
        db.commit()
        logger.info(f"Added {added} new news items to DB")
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving news: {e}")
    finally:
        db.close()

    return {"fetched": len(news_items), "added": added}

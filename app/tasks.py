from celery_worker import celery_app
from app.news_parser.sites import NewsParser
from app.news_parser.telegram import TelegramNewsParser
from app.database import SessionLocal
from app.ai.generator import generate_post_from_news
from app.models import NewsItem, Post
import logging
import asyncio

logger = logging.getLogger(__name__)


def _save_news_items(news_items: list):
    db = SessionLocal()
    added = 0
    try:
        for item in news_items:
            existing = db.query(NewsItem).filter(NewsItem.url == item["url"]).first()
            if not existing:
                db_item = NewsItem(**item)
                db.add(db_item)
                added += 1
        db.commit()
        logger.info(f"Добавлено {added} новых новостей в БД")
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка сохранения новости: {e}")
    finally:
        db.close()
    return added


@celery_app.task
def fetch_news_from_sites():
    parser = NewsParser()
    news_items = parser.parse_all()
    added = _save_news_items(news_items)
    return {"Получено": len(news_items), "Добавлено": added}


@celery_app.task
def fetch_news_from_telegram():
    parser = TelegramNewsParser()
    news_items = parser.run_sync()
    added = _save_news_items(news_items)
    return {"Получено": len(news_items), "Добавлено": added}


@celery_app.task
def generate_posts_for_unprocessed_news():
    """Генерирует посты для всех непроцессированных новостей"""
    db = SessionLocal()
    try:
        # Находим новости без постов
        news_items = db.query(NewsItem).outerjoin(Post).filter(Post.id.is_(None)).all()

        for news in news_items:
            try:
                # Генерируем пост
                result = asyncio.run(generate_post_from_news(news.summary))

                # Сохраняем в БД
                post = Post(
                    title=result["title"],
                    content=result["content"],
                    news_item_id=news.id
                )
                db.add(post)
                db.commit()
                logger.info(f"Создан пост для новости: {news.title[:50]}...")

            except Exception as e:
                logger.error(f"Не удалось сгенерировать пост для новости {news.id}: {e}")
                # Можно пометить как failed, но пока просто пропускаем

    finally:
        db.close()

    return {"processed": len(news_items)}

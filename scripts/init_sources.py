import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.api.crud import create_news_source
from app.api.schemas import NewsSourceCreate


def init_default_sources():
    db = SessionLocal()
    try:
        sources = [
            NewsSourceCreate(name="Habr", url="https://habr.com/ru/rss/articles/", parser_type="rss"),
            NewsSourceCreate(name="VC.ru", url="https://vc.ru/rss", parser_type="rss"),
            NewsSourceCreate(name="Telegram Channel", url="@your_channel", parser_type="telegram", is_active=False),
        ]

        for source in sources:
            try:
                create_news_source(db, source)
                print(f"✅ Добавлен источник: {source.name}")
            except Exception as e:
                print(f"⚠️ Источник {source.name} уже существует")

    finally:
        db.close()


if __name__ == "__main__":
    init_default_sources()

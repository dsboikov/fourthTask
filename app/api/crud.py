from sqlalchemy.orm import Session
from app.models import NewsItem
from app.api.schemas import NewsItemCreate, NewsItemUpdate
import uuid


def get_news_item(db: Session, news_id: uuid.UUID):
    return db.query(NewsItem).filter(NewsItem.id == news_id).first()


def get_news_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(NewsItem).offset(skip).limit(limit).all()


def create_news_item(db: Session, news: NewsItemCreate):
    db_news = NewsItem(**news.model_dump())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news


def update_news_item(db: Session, news_id: uuid.UUID, news_update: NewsItemUpdate):
    db_news = get_news_item(db, news_id)
    if not db_news:
        return None
    for key, value in news_update.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(db_news, key, value)
    db.commit()
    db.refresh(db_news)
    return db_news


def delete_news_item(db: Session, news_id: uuid.UUID):
    db_news = get_news_item(db, news_id)
    if not db_news:
        return False
    db.delete(db_news)
    db.commit()
    return True

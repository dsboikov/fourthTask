from sqlalchemy.orm import Session
from app.models import NewsItem, Post
from app.api.schemas import NewsItemCreate, NewsItemUpdate, PostCreate, PostUpdate
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


def get_post(db: Session, post_id: uuid.UUID):
    return db.query(Post).filter(Post.id == post_id).first()


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Post).offset(skip).limit(limit).all()


def create_post(db: Session, post: PostCreate):
    db_post = Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def update_post(db: Session, post_id: uuid.UUID, post_update: PostUpdate):
    db_post = get_post(db, post_id)
    if not db_post:
        return None
    for key, value in post_update.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: uuid.UUID):
    db_post = get_post(db, post_id)
    if not db_post:
        return False
    db.delete(db_post)
    db.commit()
    return True

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import NewsItem, Post, NewsSource
from app.api.schemas import NewsItemCreate, NewsItemUpdate, PostCreate, PostUpdate, PostStatus, NewsSourceCreate, \
    NewsSourceUpdate
import uuid
import logging

logger = logging.getLogger(__name__)


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


def create_news_item_if_not_exists(db: Session, news_data: dict):
    # Проверяем по URL или заголовку
    existing = db.query(NewsItem).filter(
        (NewsItem.url == news_data["url"]) |
        (NewsItem.title == news_data["title"])
    ).first()

    if not existing:
        news_create = NewsItemCreate(**news_data)
        return create_news_item(db, news_create)
    else:
        logger.debug(f"Skipping duplicate: {news_data['title']}")
        return None


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
    # Проверяем, существует ли news_item
    news_item = db.query(NewsItem).filter(NewsItem.id == post.news_item_id).first()
    if not news_item:
        raise ValueError(f"NewsItem with id {post.news_item_id} not found")

    db_post = Post(**post.model_dump())
    db.add(db_post)
    try:
        db.commit()
        db.refresh(db_post)
    except IntegrityError:
        db.rollback()
        raise ValueError("Invalid news_item_id")
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


def get_posts_by_status(db: Session, status: PostStatus, skip: int = 0, limit: int = 100):
    return db.query(Post).filter(Post.status == status).offset(skip).limit(limit).all()


def retry_failed_posts(db: Session):
    """Возвращает список ID постов со статусом 'failed'"""
    posts = db.query(Post).filter(Post.status == PostStatus.failed).all()
    for post in posts:
        post.status = PostStatus.draft
    db.commit()
    return [post.id for post in posts]


def get_news_stats(db: Session):
    total = db.query(NewsItem).count()
    processed = db.query(NewsItem).join(Post).count()
    return {
        "total": total,
        "processed": processed,
        "unprocessed": total - processed
    }


def get_posts_stats(db: Session):
    total = db.query(Post).count()
    draft = db.query(Post).filter(Post.status == "draft").count()
    published = db.query(Post).filter(Post.status == "published").count()
    failed = db.query(Post).filter(Post.status == "failed").count()
    return {
        "total": total,
        "draft": draft,
        "published": published,
        "failed": failed
    }


def get_news_source(db: Session, source_id: int):
    return db.query(NewsSource).filter(NewsSource.id == source_id).first()


def get_news_sources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(NewsSource).offset(skip).limit(limit).all()


def create_news_source(db: Session, source: NewsSourceCreate):
    db_source = NewsSource(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def update_news_source(db: Session, source_id: int, source_update: NewsSourceUpdate):
    db_source = get_news_source(db, source_id)
    if not db_source:
        return None
    for key, value in source_update.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(db_source, key, value)
    db.commit()
    db.refresh(db_source)
    return db_source


def delete_news_source(db: Session, source_id: int):
    db_source = get_news_source(db, source_id)
    if not db_source:
        return False
    db.delete(db_source)
    db.commit()
    return True

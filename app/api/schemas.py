from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class NewsItemBase(BaseModel):
    title: str
    url: Optional[str] = None
    summary: str
    source: str
    published_at: datetime
    raw_text: Optional[str] = None


class NewsItemCreate(NewsItemBase):
    pass


class NewsItemUpdate(NewsItemBase):
    title: Optional[str] = None
    summary: Optional[str] = None
    raw_text: Optional[str] = None


class NewsItemRead(NewsItemBase):
    id: uuid.UUID

    class Config:
        from_attributes = True  # для SQLAlchemy 2.0+


class PostStatus(str, Enum):
    draft = "draft"
    published = "published"
    failed = "failed"


class PostBase(BaseModel):
    title: str
    content: str
    status: PostStatus = PostStatus.draft


class PostCreate(PostBase):
    news_item_id: uuid.UUID


class PostUpdate(PostBase):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None


class PostRead(PostBase):
    id: uuid.UUID
    news_item_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    news_total: int
    news_processed: int
    news_unprocessed: int

    posts_total: int
    posts_draft: int
    posts_published: int
    posts_failed: int

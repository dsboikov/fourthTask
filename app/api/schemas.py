from pydantic import BaseModel
from datetime import datetime
from typing import Optional
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


class PostBase(BaseModel):
    title: str
    content: str
    status: Optional[str] = "draft"


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

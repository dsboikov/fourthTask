from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    url = Column(String, nullable=True)
    summary = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False, default=datetime.now)
    raw_text = Column(Text, nullable=True)

    def __repr__(self):
        return f"<NewsItem(title='{self.title[:30]}...', source='{self.source}')>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "source": self.source,
            "published_at": self.published_at.isoformat(),
            "raw_text": self.raw_text
        }


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, default="draft")  # draft, published, failed
    news_item_id = Column(UUID(as_uuid=True), ForeignKey("news_items.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Post(title='{self.title[:30]}...', status='{self.status}')>"


class NewsSource(Base):
    __tablename__ = "news_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    parser_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import text
from app.database import get_db
from app.config import settings
from app.logging_config import setup_logging
from sqlalchemy.orm import Session
from app.api import crud, schemas
import uuid

setup_logging()
app = FastAPI(title="AI Telegram Post Generator")


@app.get("/")
def root():
    return {
        "status": "ok",
        "openai_key_set": bool(settings.OPENAI_API_KEY),
        "telegram_configured": bool(settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH),
        "db_url_sample": settings.DATABASE_URL[:30] + "...",
    }


@app.get("/health/db")
def health_db(db=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}


@app.get("/news/", response_model=list[schemas.NewsItemRead])
def read_news_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_news_items(db, skip=skip, limit=limit)


@app.get("/news/{news_id}", response_model=schemas.NewsItemRead)
def read_news_item(news_id: str, db: Session = Depends(get_db)):
    try:
        news_uuid = uuid.UUID(news_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    news = crud.get_news_item(db, news_uuid)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return news


@app.post("/news/", response_model=schemas.NewsItemRead, status_code=status.HTTP_201_CREATED)
def create_news_item(news: schemas.NewsItemCreate, db: Session = Depends(get_db)):
    return crud.create_news_item(db, news)


@app.put("/news/{news_id}", response_model=schemas.NewsItemRead)
def update_news_item(news_id: str, news_update: schemas.NewsItemUpdate, db: Session = Depends(get_db)):
    try:
        news_uuid = uuid.UUID(news_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    news = crud.update_news_item(db, news_uuid, news_update)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return news


@app.delete("/news/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news_item(news_id: str, db: Session = Depends(get_db)):
    try:
        news_uuid = uuid.UUID(news_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    success = crud.delete_news_item(db, news_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="News item not found")

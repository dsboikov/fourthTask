from fastapi import FastAPI, Depends
from sqlalchemy import text
from app.database import get_db
from app.config import settings
from app.logging_config import setup_logging

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

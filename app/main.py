from fastapi import FastAPI
from app.config import settings

app = FastAPI(title="AI Telegram Post Generator")


@app.get("/")
def root():
    return {
        "status": "ok",
        "openai_key_set": bool(settings.OPENAI_API_KEY),
        "telegram_configured": bool(settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH),
        "db_url_sample": settings.DATABASE_URL[:30] + "...",
    }

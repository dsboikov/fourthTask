import os


class Settings:
    # Telegram
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID", "0"))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_SESSION_NAME: str = os.getenv("TELEGRAM_SESSION_NAME", "aibot_session")
    TELEGRAM_CHANNEL_USERNAME: str = os.getenv("TELEGRAM_CHANNEL_USERNAME", "")
    MAX_POSTS_PER_PUBLISH: int = int(os.getenv("MAX_POSTS_PER_PUBLISH", "5"))

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/aibotdb")

    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", f"{REDIS_URL}/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", f"{REDIS_URL}/1")
    OPENAI_PROXY_URL: str = os.getenv("OPENAI_PROXY_URL", "")


# Экземпляр настроек
settings = Settings()

from pathlib import Path
from dotenv import load_dotenv
import os

# Загружаем .env из корня проекта
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    # Telegram
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID", "0"))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_SESSION_NAME: str = os.getenv("TELEGRAM_SESSION_NAME", "aibot_session")
    TELEGRAM_CHANNEL_USERNAME: str = os.getenv("TELEGRAM_CHANNEL_USERNAME", "")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Определяем, запущены ли мы в Docker
    IN_DOCKER = os.getenv("IN_DOCKER", "false").lower() == "true"

    # Database
    DATABASE_URL: str = (
        os.getenv("DATABASE_URL_DOCKER")
        if IN_DOCKER
        else os.getenv("DATABASE_URL_LOCAL", "postgresql+psycopg://postgres:postgres@localhost:5432/aibotdb")
    )

    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL + "/1")


# Экземпляр настроек
settings = Settings()

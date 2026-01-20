from celery import Celery
from app.config import settings
from app.logging_config import setup_logging

setup_logging()

celery_app = Celery(
    "aibot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Автоматически обнаруживать задачи в app.tasks
celery_app.autodiscover_tasks(["app"])
# Периодические задачи
celery_app.conf.beat_schedule = {
    "fetch-news-sites": {
        "task": "app.tasks.fetch_news_from_sites",
        "schedule": 30 * 60,  # каждые 30 минут
    },
    "fetch-news-telegram": {
        "task": "app.tasks.fetch_news_from_telegram",
        "schedule": 30 * 60,
    },
}

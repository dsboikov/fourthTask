from celery import Celery
from app.config import settings

celery_app = Celery(
    "aibot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Автоматически обнаруживать задачи в app.tasks
celery_app.autodiscover_tasks(["app"])

from celery_worker import celery_app

@celery_app.task
def test_task():
    return "Celery works!"

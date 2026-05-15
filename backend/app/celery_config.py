from celery import Celery

celery_app = Celery(
    "judge",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5分钟
    worker_prefetch_multiplier=1,
)

celery_app.autodiscover_tasks(["app.tasks"])

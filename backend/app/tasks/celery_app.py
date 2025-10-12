from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "flyinghotel",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TZ,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    result_expires=3600,  # 1 hour
)

# Auto-discover tasks from all modules
celery_app.autodiscover_tasks([
    "app.tasks",
])

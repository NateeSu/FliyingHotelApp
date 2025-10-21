"""
Celery Tasks Module
Import all task modules here for autodiscovery
"""
from app.tasks.celery_app import celery_app
from app.tasks import booking_tasks

__all__ = ["celery_app", "booking_tasks"]

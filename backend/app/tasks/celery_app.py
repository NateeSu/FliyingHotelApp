from celery import Celery
from celery.schedules import crontab
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

# Celery Beat Schedule (Phase 7: Booking System)
celery_app.conf.beat_schedule = {
    # Check bookings for today and update room status to 'reserved'
    # Runs daily at 00:01 Thai time
    'check-bookings-for-today': {
        'task': 'booking.check_bookings_for_today',
        'schedule': crontab(hour=0, minute=1),
    },
    # Check if guests have checked in on time
    # Runs every 30 minutes
    'check-booking-check-in-times': {
        'task': 'booking.check_booking_check_in_times',
        'schedule': crontab(minute='*/30'),
    },
}

# Auto-discover tasks from all modules
celery_app.autodiscover_tasks([
    "app.tasks",
])

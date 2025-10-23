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
    timezone=settings.TZ,  # Asia/Bangkok
    enable_utc=False,  # Use local timezone (Asia/Bangkok) instead of UTC
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    result_expires=3600,  # 1 hour
)

# Celery Beat Schedule
celery_app.conf.beat_schedule = {
    # Phase 7: Check bookings for today and update room status to 'reserved'
    # Runs daily at 00:01 Thai time
    'check-bookings-for-today': {
        'task': 'booking.check_bookings_for_today',
        'schedule': crontab(hour=0, minute=1),
    },
    # Phase 7: Check if guests have checked in on time
    # Runs every 30 minutes
    'check-booking-check-in-times': {
        'task': 'booking.check_booking_check_in_times',
        'schedule': crontab(minute='*/30'),
    },
    # Phase 8: Send daily summary report
    # Runs every day at 8:00 AM Thai time
    'send-daily-summary-report': {
        'task': 'send_daily_summary_report',
        'schedule': crontab(hour=8, minute=0),
    },
}

# Auto-discover tasks from all modules
celery_app.autodiscover_tasks([
    "app.tasks",
])

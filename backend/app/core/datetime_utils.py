"""
Datetime utilities for timezone-aware operations
All timestamps use Asia/Bangkok timezone as specified in CLAUDE.md

Note: Returns naive datetime (without timezone info) for database compatibility
while calculating time in Bangkok timezone.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Thailand timezone
BANGKOK_TZ = ZoneInfo("Asia/Bangkok")


def now_thailand() -> datetime:
    """
    Get current datetime in Thailand timezone (Asia/Bangkok)

    Returns naive datetime (without tzinfo) for database compatibility,
    but calculated in Bangkok timezone.

    Returns:
        naive datetime object representing current time in Bangkok
    """
    # Get timezone-aware datetime in Bangkok, then remove tzinfo
    return datetime.now(BANGKOK_TZ).replace(tzinfo=None)


def to_thailand_tz(dt: datetime) -> datetime:
    """
    Convert any datetime to Thailand timezone

    Args:
        dt: datetime object (can be naive or timezone-aware)

    Returns:
        timezone-aware datetime in Bangkok timezone
    """
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(BANGKOK_TZ)


def make_aware(dt: datetime) -> datetime:
    """
    Make naive datetime timezone-aware in Bangkok timezone

    Args:
        dt: naive datetime

    Returns:
        timezone-aware datetime in Bangkok timezone
    """
    if dt.tzinfo is not None:
        # Already aware, convert to Bangkok
        return dt.astimezone(BANGKOK_TZ)

    # Treat as Bangkok time
    return dt.replace(tzinfo=BANGKOK_TZ)

"""
Breaker Celery Tasks

Automated background tasks for breaker management:
1. Periodic status synchronization (every 30 seconds)
2. Process control queue (debouncing and retries)
3. Health check and error monitoring
"""
from celery import shared_task
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
from typing import List

from app.db.session import AsyncSessionLocal
from app.models.home_assistant import (
    HomeAssistantBreaker,
    BreakerControlQueue,
    QueueStatus,
    TargetState,
    TriggerType
)
from app.services.breaker_service import BreakerService
from app.services.home_assistant_service import HomeAssistantService
from app.core.websocket import websocket_manager
from app.core.exceptions import HomeAssistantException


@shared_task(name="breaker.sync_all_breaker_states")
def sync_all_breaker_states():
    """
    Celery task: Sync all breaker states from Home Assistant.

    Schedule: Every 30 seconds

    Actions:
    - Query all active breakers
    - Fetch current state from Home Assistant
    - Update database
    - Broadcast WebSocket event if state changed
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async_sync_all_breaker_states())
    finally:
        loop.close()


async def _async_sync_all_breaker_states():
    """Async implementation of sync_all_breaker_states"""
    async with AsyncSessionLocal() as db:
        try:
            breaker_service = BreakerService(db)
            result = await breaker_service.sync_all_breakers()

            # Broadcast WebSocket event
            await websocket_manager.broadcast({
                "event": "breaker_states_synced",
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "total": result["total"],
                    "success_count": result["success_count"],
                    "failed_count": result["failed_count"]
                }
            })

            return {
                "success": True,
                "message": result["message"],
                "synced_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }


@shared_task(name="breaker.process_control_queue")
def process_control_queue():
    """
    Celery task: Process pending control queue items.

    Schedule: Every 5 seconds

    Actions:
    - Find queue items where scheduled_at <= NOW and status = PENDING
    - Execute commands (turn on/off)
    - Update queue status to COMPLETED or FAILED
    - Retry failed commands (up to max_retries)
    - Broadcast WebSocket events
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async_process_control_queue())
    finally:
        loop.close()


async def _async_process_control_queue():
    """Async implementation of process_control_queue"""
    async with AsyncSessionLocal() as db:
        try:
            # Find pending queue items ready for execution
            now = datetime.now()
            stmt = select(BreakerControlQueue).where(
                and_(
                    BreakerControlQueue.scheduled_at <= now,
                    BreakerControlQueue.status == QueueStatus.PENDING
                )
            ).order_by(
                BreakerControlQueue.priority,  # Higher priority first
                BreakerControlQueue.scheduled_at
            ).limit(50)  # Process max 50 items per run

            result = await db.execute(stmt)
            queue_items = list(result.scalars().all())

            if not queue_items:
                return {
                    "success": True,
                    "message": "No pending queue items",
                    "processed": 0
                }

            breaker_service = BreakerService(db)
            processed_count = 0
            success_count = 0
            failed_count = 0

            for queue_item in queue_items:
                # Mark as processing
                queue_item.status = QueueStatus.PROCESSING
                await db.commit()

                try:
                    # Get room status if available
                    breaker = await breaker_service.get_by_id(queue_item.breaker_id)
                    room_status_before = None
                    room_status_after = None

                    if breaker and breaker.room:
                        room_status_before = breaker.room.status.value
                        room_status_after = breaker.room.status.value

                    # Execute command
                    if queue_item.target_state == TargetState.ON:
                        await breaker_service.turn_on(
                            breaker_id=queue_item.breaker_id,
                            trigger_type=queue_item.trigger_type,
                            triggered_by=queue_item.triggered_by,
                            room_status_before=room_status_before,
                            room_status_after=room_status_after
                        )
                    else:
                        await breaker_service.turn_off(
                            breaker_id=queue_item.breaker_id,
                            trigger_type=queue_item.trigger_type,
                            triggered_by=queue_item.triggered_by,
                            room_status_before=room_status_before,
                            room_status_after=room_status_after
                        )

                    # Mark as completed
                    queue_item.status = QueueStatus.COMPLETED
                    queue_item.error_message = None
                    await db.commit()

                    success_count += 1
                    processed_count += 1

                    # Broadcast WebSocket event
                    await websocket_manager.broadcast({
                        "event": "breaker_state_changed",
                        "data": {
                            "breaker_id": queue_item.breaker_id,
                            "entity_id": breaker.entity_id if breaker else None,
                            "new_state": queue_item.target_state.value,
                            "trigger_type": queue_item.trigger_type.value,
                            "timestamp": datetime.now().isoformat()
                        }
                    })

                except Exception as e:
                    # Handle failure
                    queue_item.retry_count += 1
                    queue_item.error_message = str(e)

                    if queue_item.retry_count >= queue_item.max_retries:
                        # Max retries reached, mark as failed
                        queue_item.status = QueueStatus.FAILED
                        failed_count += 1
                        processed_count += 1
                    else:
                        # Retry with exponential backoff
                        queue_item.status = QueueStatus.PENDING
                        queue_item.scheduled_at = now + timedelta(seconds=3 * (queue_item.retry_count + 1))

                    await db.commit()

            return {
                "success": True,
                "message": f"Processed {processed_count} queue items",
                "processed": processed_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "processed_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }


@shared_task(name="breaker.health_check")
def health_check():
    """
    Celery task: Health check for Home Assistant connection and breakers.

    Schedule: Every 5 minutes

    Actions:
    - Test Home Assistant connection
    - Update config status
    - Check breakers with consecutive errors >= 3
    - Send admin notification if issues found
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async_health_check())
    finally:
        loop.close()


async def _async_health_check():
    """Async implementation of health_check"""
    async with AsyncSessionLocal() as db:
        try:
            ha_service = HomeAssistantService(db)

            # Test connection
            try:
                test_result = await ha_service.test_connection()
                is_online = test_result.get("success", False)
                ha_version = test_result.get("ha_version")

                # Update config status
                await ha_service.update_config_status(
                    is_online=is_online,
                    ha_version=ha_version
                )

            except HomeAssistantException as e:
                # Home Assistant is offline
                await ha_service.update_config_status(is_online=False)
                return {
                    "success": False,
                    "ha_online": False,
                    "error": str(e),
                    "checked_at": datetime.now().isoformat()
                }

            # Check breakers with errors
            stmt = select(HomeAssistantBreaker).where(
                and_(
                    HomeAssistantBreaker.is_active == True,
                    HomeAssistantBreaker.consecutive_errors >= 3
                )
            )
            result = await db.execute(stmt)
            breakers_with_errors = list(result.scalars().all())

            if breakers_with_errors:
                # TODO: Send notification to admin via Telegram
                # from app.services.notification_service import NotificationService
                # notification_service = NotificationService(db)
                # await notification_service.send_breaker_error_alert(breakers_with_errors)
                pass

            return {
                "success": True,
                "ha_online": is_online,
                "ha_version": ha_version,
                "breakers_with_errors": len(breakers_with_errors),
                "error_entities": [b.entity_id for b in breakers_with_errors],
                "checked_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }


@shared_task(name="breaker.cleanup_old_queue_items")
def cleanup_old_queue_items():
    """
    Celery task: Clean up old completed/failed queue items.

    Schedule: Daily at 3:00 AM

    Actions:
    - Delete queue items older than 7 days with status COMPLETED or FAILED
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async_cleanup_old_queue_items())
    finally:
        loop.close()


async def _async_cleanup_old_queue_items():
    """Async implementation of cleanup_old_queue_items"""
    async with AsyncSessionLocal() as db:
        try:
            # Delete items older than 7 days
            cutoff_date = datetime.now() - timedelta(days=7)

            stmt = select(BreakerControlQueue).where(
                and_(
                    BreakerControlQueue.created_at < cutoff_date,
                    or_(
                        BreakerControlQueue.status == QueueStatus.COMPLETED,
                        BreakerControlQueue.status == QueueStatus.FAILED
                    )
                )
            )

            result = await db.execute(stmt)
            old_items = list(result.scalars().all())

            for item in old_items:
                await db.delete(item)

            await db.commit()

            return {
                "success": True,
                "message": f"Deleted {len(old_items)} old queue items",
                "deleted_count": len(old_items),
                "cleaned_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }


@shared_task(name="breaker.cleanup_old_activity_logs")
def cleanup_old_activity_logs():
    """
    Celery task: Clean up old activity logs.

    Schedule: Weekly on Sunday at 4:00 AM

    Actions:
    - Delete activity logs older than 90 days
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async_cleanup_old_activity_logs())
    finally:
        loop.close()


async def _async_cleanup_old_activity_logs():
    """Async implementation of cleanup_old_activity_logs"""
    from app.models.home_assistant import BreakerActivityLog

    async with AsyncSessionLocal() as db:
        try:
            # Delete logs older than 90 days
            cutoff_date = datetime.now() - timedelta(days=90)

            stmt = select(BreakerActivityLog).where(
                BreakerActivityLog.created_at < cutoff_date
            )

            result = await db.execute(stmt)
            old_logs = list(result.scalars().all())

            for log in old_logs:
                await db.delete(log)

            await db.commit()

            return {
                "success": True,
                "message": f"Deleted {len(old_logs)} old activity logs",
                "deleted_count": len(old_logs),
                "cleaned_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }

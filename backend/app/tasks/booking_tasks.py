"""
Booking Celery Tasks (Phase 7)
Automated tasks for booking system:
1. Auto-update room status on booking date
2. Send reminders for overdue bookings
"""
from celery import shared_task
from sqlalchemy import select, and_
from datetime import date, datetime, timedelta
from typing import List

from app.db.session import AsyncSessionLocal
from app.models.booking import Booking, BookingStatusEnum
from app.models.room import Room, RoomStatus
from app.models.check_in import CheckIn
from app.core.datetime_utils import now_thailand, today_thailand
from app.core.websocket import websocket_manager


@shared_task(name="booking.check_bookings_for_today")
def check_bookings_for_today():
    """
    Celery task: Check bookings for today and update room status to 'reserved'

    Schedule: Daily at 00:01 Thai time

    Actions:
    - Find all confirmed bookings where check_in_date = TODAY
    - Update room status from 'available' → 'reserved'
    - Broadcast WebSocket event
    """
    import asyncio
    return asyncio.run(_async_check_bookings_for_today())


async def _async_check_bookings_for_today():
    """Async implementation of check_bookings_for_today"""
    async with AsyncSessionLocal() as db:
        try:
            # Use Thailand timezone for accurate date
            today = today_thailand()

            # Find confirmed bookings for today
            stmt = select(Booking).where(
                and_(
                    Booking.check_in_date == today,
                    Booking.status == BookingStatusEnum.CONFIRMED
                )
            )

            result = await db.execute(stmt)
            bookings = result.scalars().all()

            updated_count = 0

            for booking in bookings:
                # Get room
                room = await db.get(Room, booking.room_id)

                if room and room.status == RoomStatus.AVAILABLE:
                    # Update room status to reserved
                    old_status = room.status
                    room.status = RoomStatus.RESERVED

                    await db.commit()
                    updated_count += 1

                    # Broadcast WebSocket event
                    await websocket_manager.broadcast({
                        "event": "room_status_changed",
                        "data": {
                            "room_id": room.id,
                            "old_status": old_status.value,
                            "new_status": RoomStatus.RESERVED.value,
                            "timestamp": now_thailand().isoformat(),
                            "reason": "booking_check_in_date"
                        }
                    })

                    print(f"✅ Updated room {room.room_number} to RESERVED (Booking #{booking.id})")

            print(f"📅 check_bookings_for_today completed: {updated_count} rooms updated")
            return {
                "success": True,
                "date": today.isoformat(),
                "bookings_found": len(bookings),
                "rooms_updated": updated_count
            }

        except Exception as e:
            print(f"❌ Error in check_bookings_for_today: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }


@shared_task(name="booking.check_booking_check_in_times")
def check_booking_check_in_times():
    """
    Celery task: Check if guests have checked in on time

    Schedule: Every 30 minutes

    Actions:
    - Find confirmed bookings where:
      - check_in_date = TODAY
      - Expected check-in time passed by > 1 hour
      - No associated check_in record
    - Send Telegram reminder to admin/reception
    """
    import asyncio
    return asyncio.run(_async_check_booking_check_in_times())


async def _async_check_booking_check_in_times():
    """Async implementation of check_booking_check_in_times"""
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as db:
        try:
            # Use Thailand timezone for accurate date and time
            today = today_thailand()
            now = now_thailand()

            # Typical check-in time is 14:00
            # If it's before 15:00, don't check yet
            if now.hour < 15:
                print("⏰ Too early to check for overdue bookings (before 15:00)")
                return {
                    "success": True,
                    "message": "Too early to check",
                    "current_time": now.isoformat()
                }

            # Find confirmed bookings for today
            stmt = select(Booking).options(
                selectinload(Booking.customer),
                selectinload(Booking.room),
                selectinload(Booking.check_ins)
            ).where(
                and_(
                    Booking.check_in_date == today,
                    Booking.status == BookingStatusEnum.CONFIRMED
                )
            )

            result = await db.execute(stmt)
            bookings = result.scalars().all()

            overdue_bookings = []

            for booking in bookings:
                # Check if booking has any check-in records
                if booking.check_ins and len(booking.check_ins) > 0:
                    # Guest has checked in
                    continue

                # Calculate how long overdue (assume check-in time is 14:00)
                check_in_datetime = datetime.combine(today, datetime.min.time()).replace(hour=14, minute=0)
                time_diff = now - check_in_datetime

                # If more than 1 hour overdue
                if time_diff.total_seconds() > 3600:  # 1 hour in seconds
                    overdue_minutes = int(time_diff.total_seconds() / 60)
                    overdue_bookings.append({
                        "booking": booking,
                        "overdue_minutes": overdue_minutes
                    })

            # Send Telegram notifications for overdue bookings
            if overdue_bookings:
                await _send_overdue_booking_notifications(overdue_bookings, db)

            print(f"📋 check_booking_check_in_times completed: {len(overdue_bookings)} overdue bookings found")
            return {
                "success": True,
                "current_time": now.isoformat(),
                "total_bookings": len(bookings),
                "overdue_bookings": len(overdue_bookings)
            }

        except Exception as e:
            print(f"❌ Error in check_booking_check_in_times: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }


async def _send_overdue_booking_notifications(overdue_bookings: List[dict], db):
    """
    Send Telegram notifications for overdue bookings

    Args:
        overdue_bookings: List of dicts with 'booking' and 'overdue_minutes'
        db: Database session
    """
    try:
        from app.services.telegram_service import TelegramService

        telegram_service = TelegramService(db)

        for item in overdue_bookings:
            booking = item['booking']
            overdue_minutes = item['overdue_minutes']

            # Format overdue time
            hours = overdue_minutes // 60
            mins = overdue_minutes % 60
            overdue_str = f"{hours} ชั่วโมง {mins} นาที" if hours > 0 else f"{mins} นาที"

            # Prepare message
            message = f"""⚠️ **การจองเลยเวลา Check-in**

📅 Booking ID: #{booking.id}
🏠 ห้อง: {booking.room.room_number}
👤 ลูกค้า: {booking.customer.full_name}
📞 โทร: {booking.customer.phone_number}
📆 วันที่จอง: {booking.check_in_date.strftime('%d/%m/%Y')} (14:00)
⏰ เลยเวลามาแล้ว: {overdue_str}

💰 เงินมัดจำ: {booking.deposit_amount:,.2f} บาท
💵 ยอดรวม: {booking.total_amount:,.2f} บาท

กรุณาติดต่อลูกค้าเพื่อยืนยันการเข้าพัก หรือพิจารณายกเลิกการจอง
"""

            # Send to admin and reception groups
            await telegram_service.send_notification(
                message=message,
                target_roles=["ADMIN", "RECEPTION"],
                notification_type="booking_overdue"
            )

            print(f"📱 Sent overdue notification for Booking #{booking.id}")

    except Exception as e:
        print(f"❌ Error sending overdue booking notifications: {str(e)}")
        import traceback
        traceback.print_exc()

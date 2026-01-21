"""
Overtime Celery Tasks
Automated tasks for monitoring and processing overtime temporary stays
"""
from celery import shared_task

from app.db.session import AsyncSessionLocal
from app.services.overtime_service import OvertimeService


@shared_task(name="overtime.check_and_process_overtime")
def check_and_process_overtime():
    """
    Celery task: Check and process overtime temporary stays

    Schedule: Every 1 minute

    Actions:
    - Find all TEMPORARY stays where:
      - status = CHECKED_IN
      - current_time > expected_check_out_time
      - is_overtime = 0 (not already marked)
    - Update is_overtime flag
    - Update room status to OCCUPIED_OVERTIME
    - Broadcast WebSocket event for real-time UI update
    - Smart breaker will be automatically turned OFF by breaker automation

    Returns:
        Dict with processing results
    """
    import asyncio
    return asyncio.run(_async_check_and_process_overtime())


async def _async_check_and_process_overtime():
    """Async implementation of check_and_process_overtime"""
    async with AsyncSessionLocal() as db:
        try:
            overtime_service = OvertimeService(db)
            result = await overtime_service.check_and_process_overtime_stays()

            if result["rooms_updated"] > 0:
                print(f"⏰ [OVERTIME TASK] Processed {result['rooms_updated']} overtime rooms")
                print(f"   Check-ins: {result['processed_check_ins']}")
            else:
                print(f"✅ [OVERTIME TASK] No overtime stays found")

            # After updating room status to OCCUPIED_OVERTIME,
            # the breaker automation in breaker_service.py will automatically
            # turn OFF the smart breaker for those rooms

            # Send Telegram notifications for overtime rooms
            if result["rooms_updated"] > 0:
                await _send_overtime_notifications(result["processed_check_ins"], db)

            return result

        except Exception as e:
            print(f"❌ Error in check_and_process_overtime task: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }


async def _send_overtime_notifications(check_in_ids: list, db):
    """
    Send Telegram notifications for overtime stays

    Args:
        check_in_ids: List of check-in IDs that went overtime
        db: Database session
    """
    try:
        from app.services.telegram_service import TelegramService
        from app.models.check_in import CheckIn
        from sqlalchemy.orm import selectinload

        telegram_service = TelegramService(db)

        for check_in_id in check_in_ids:
            # Fetch check-in with relationships
            check_in = await db.get(
                CheckIn,
                check_in_id,
                options=[
                    selectinload(CheckIn.room),
                    selectinload(CheckIn.customer)
                ]
            )

            if not check_in:
                continue

            # Format overtime duration
            hours = check_in.overtime_minutes // 60
            mins = check_in.overtime_minutes % 60
            overtime_str = f"{hours} ชั่วโมง {mins} นาที" if hours > 0 else f"{mins} นาที"

            # Prepare message
            message = f"""⚠️ **หมดเวลาเข้าพัก - ตัดไฟอัตโนมัติ**

🏠 ห้อง: {check_in.room.room_number}
👤 ลูกค้า: {check_in.customer.full_name if check_in.customer else 'N/A'}
📞 โทร: {check_in.customer.phone_number if check_in.customer else 'N/A'}
⏰ เข้าพัก: {check_in.check_in_time.strftime('%H:%M น.')}
⏰ หมดเวลา: {check_in.expected_check_out_time.strftime('%H:%M น.')}
⏱️ เกินเวลามาแล้ว: {overtime_str}

🔌 **ระบบได้ตัดไฟห้องอัตโนมัติแล้ว**

กรุณาติดต่อลูกค้าเพื่อดำเนินการ Check-out หรือเปลี่ยนประเภทการเข้าพัก
"""

            # Send to admin and reception groups
            await telegram_service.send_notification(
                message=message,
                target_roles=["ADMIN", "RECEPTION"],
                notification_type="overtime_alert"
            )

            print(f"📱 Sent overtime notification for Check-in #{check_in_id}, Room {check_in.room.room_number}")

    except Exception as e:
        print(f"❌ Error sending overtime notifications: {str(e)}")
        import traceback
        traceback.print_exc()

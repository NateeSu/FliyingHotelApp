"""
Report Tasks (Phase 8)
Celery tasks for automated report generation and distribution
"""
from celery import shared_task
from datetime import date, datetime, timedelta
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.reports_service import ReportsService
from app.services.settings_service import SettingsService
from app.services.telegram_service import TelegramService
import asyncio


@celery_app.task(name="send_daily_summary_report")
def send_daily_summary_report():
    """
    Send daily summary report to admin group via Telegram

    Schedule: Every day at 8:00 AM Thai time

    Report includes:
    - Total revenue (yesterday)
    - Check-ins/Check-outs (yesterday)
    - Occupancy rate (yesterday)
    - New bookings (yesterday)
    """
    asyncio.run(_send_daily_summary_report_async())


async def _send_daily_summary_report_async():
    """Async implementation of daily summary report"""
    async with AsyncSessionLocal() as db:
        try:
            # Get yesterday's date
            today = date.today()
            yesterday = today - timedelta(days=1)

            # Get reports data
            reports_service = ReportsService(db)
            summary = await reports_service.get_summary_report(yesterday, yesterday)

            # Get Telegram settings
            settings_service = SettingsService(db)
            telegram_settings = await settings_service.get_telegram_settings()

            if not telegram_settings.get('enabled'):
                print("Telegram is disabled, skipping daily summary")
                return

            admin_chat_id = telegram_settings.get('admin_chat_id')
            if not admin_chat_id:
                print("No admin chat ID configured, skipping daily summary")
                return

            # Format message
            message = f"""
📊 **สรุปประจำวัน** - {yesterday.strftime('%d/%m/%Y')}

💰 **รายได้**
   └ รวม: ฿{summary.total_revenue:,.2f}
   └ เฉลี่ย/รายการ: ฿{summary.total_revenue / summary.total_checkins if summary.total_checkins > 0 else 0:,.2f}

🏨 **อัตราเข้าพัก**
   └ {summary.occupancy_rate:.1f}% ของห้องทั้งหมด

📥 **เช็คอิน/เช็คเอาท์**
   └ เช็คอิน: {summary.total_checkins} ครั้ง
   └ เช็คเอาท์: {summary.total_checkouts} ครั้ง

📅 **การจอง**
   └ การจองใหม่: {summary.total_bookings} รายการ

👥 **ลูกค้า**
   └ ลูกค้าใหม่: {summary.new_customers} คน

---
⏰ รายงาน ณ เวลา: {datetime.now().strftime('%H:%M น.')}
🔗 ดูรายละเอียดเพิ่มเติม: [Dashboard](http://localhost:5173/reports)
            """.strip()

            # Send via Telegram
            telegram_service = TelegramService(db)
            bot_token = telegram_settings.get('bot_token')

            if bot_token:
                success = await telegram_service.send_message_direct(
                    bot_token=bot_token,
                    chat_id=admin_chat_id,
                    message=message
                )

                if success:
                    print(f"Daily summary sent successfully for {yesterday}")
                else:
                    print(f"Failed to send daily summary for {yesterday}")
            else:
                print("No bot token configured")

        except Exception as e:
            print(f"Error sending daily summary report: {str(e)}")
            import traceback
            traceback.print_exc()

"""
Telegram Service
Service for sending Telegram notifications using HTTP API
No external library required - uses aiohttp directly
"""
import aiohttp
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.settings_service import SettingsService


class TelegramService:
    """Service for Telegram Bot API integration"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings_service = SettingsService(db)

    async def get_bot_info(self, bot_token: str) -> Optional[Dict]:
        """Get bot information using getMe API"""
        url = f"https://api.telegram.org/bot{bot_token}/getMe"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    data = await response.json()
                    if data.get("ok"):
                        return data.get("result")
                    return None
            except Exception as e:
                print(f"Error getting bot info: {e}")
                return None

    async def send_message(
        self,
        chat_id: str,
        message: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = False
    ) -> bool:
        """Send a message to a Telegram chat"""
        settings = await self.settings_service.get_telegram_settings()

        if not settings.enabled or not settings.bot_token or not chat_id:
            print("Telegram not enabled or missing configuration")
            return False

        url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    data = await response.json()
                    return data.get("ok", False)
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
                return False

    async def send_housekeeping_notification(
        self,
        task_id: int,
        room_number: str,
        room_type: str,
        frontend_url: str = "http://localhost:5173"
    ):
        """Send notification for new housekeeping task"""
        settings = await self.settings_service.get_telegram_settings()

        if not settings.housekeeping_chat_id:
            print("Housekeeping chat ID not configured")
            return False

        # Use public task detail page (no login required)
        task_url = f"{frontend_url}/public/housekeeping/tasks/{task_id}"

        message = (
            f"🧹 <b>มีงานทำความสะอาดใหม่</b>\n\n"
            f"🏨 ห้อง: <b>{room_number}</b> ({room_type})\n"
            f"📋 งาน ID: <b>{task_id}</b>\n\n"
            f"🔗 <a href=\"{task_url}\">คลิกเพื่อดูรายละเอียดและรับงาน</a>\n\n"
            f"📎 URL สำหรับ Copy:\n<code>{task_url}</code>"
        )

        return await self.send_message(settings.housekeeping_chat_id, message)

    async def send_maintenance_notification(
        self,
        task_id: int,
        title: str,
        room_number: str,
        category: str,
        priority: str,
        frontend_url: str = "http://localhost:5173"
    ):
        """Send notification for new maintenance task"""
        settings = await self.settings_service.get_telegram_settings()

        if not settings.maintenance_chat_id:
            print("Maintenance chat ID not configured")
            return False

        # Use public task detail page (no login required)
        task_url = f"{frontend_url}/public/maintenance/tasks/{task_id}"

        priority_emoji = {
            "urgent": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(priority, "⚪")

        message = (
            f"🔧 <b>มีงานซ่อมบำรุงใหม่</b>\n\n"
            f"📋 {title}\n"
            f"🏨 ห้อง: <b>{room_number}</b>\n"
            f"🔖 ประเภท: {category}\n"
            f"{priority_emoji} ลำดับความสำคัญ: {priority}\n"
            f"📋 งาน ID: <b>{task_id}</b>\n\n"
            f"🔗 <a href=\"{task_url}\">คลิกเพื่อดูรายละเอียดและรับงาน</a>\n\n"
            f"📎 URL สำหรับ Copy:\n<code>{task_url}</code>"
        )

        return await self.send_message(settings.maintenance_chat_id, message)

    async def test_connection(self, bot_token: str, chat_id: str) -> tuple[bool, str, Optional[Dict]]:
        """Test Telegram bot connection and send test message"""
        # First, test if bot token is valid
        bot_info = await self.get_bot_info(bot_token)

        if not bot_info:
            return False, "Invalid bot token or cannot connect to Telegram API", None

        # Try to send a test message
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": "✅ การเชื่อมต่อ Telegram Bot สำเร็จ!\n\nระบบ FlyingHotelApp พร้อมส่งการแจ้งเตือนแล้ว",
            "parse_mode": "HTML"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    data = await response.json()

                    if data.get("ok"):
                        return True, f"Connected successfully! Bot: {bot_info.get('first_name', 'Unknown')}", bot_info
                    else:
                        error_desc = data.get("description", "Unknown error")
                        return False, f"Failed to send message: {error_desc}", bot_info

            except Exception as e:
                return False, f"Connection error: {str(e)}", bot_info

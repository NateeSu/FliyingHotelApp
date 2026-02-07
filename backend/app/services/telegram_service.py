"""
Telegram Service
Service for sending Telegram notifications using HTTP API
No external library required - uses aiohttp directly
"""
import logging
import aiohttp
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)


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
                logger.error("Error getting bot info: %s", e)
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

        if not settings.enabled:
            logger.debug("Telegram notifications are disabled in settings")
            return False

        if not settings.bot_token:
            logger.warning("Telegram Bot Token is not set")
            return False

        if not chat_id:
            logger.warning("Chat ID is empty")
            return False

        url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }

        logger.info("Sending Telegram message to chat_id: %s", chat_id)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    data = await response.json()

                    if data.get("ok"):
                        logger.info("Telegram message sent successfully")
                        return True
                    else:
                        error_desc = data.get("description", "Unknown error")
                        logger.error("Telegram API error: %s", error_desc)
                        return False

            except Exception as e:
                logger.exception("Error sending Telegram message")
                return False

    async def send_housekeeping_notification(
        self,
        task_id: int,
        room_number: str,
        room_type: str,
        frontend_url: str = None
    ):
        """Send notification for new housekeeping task"""
        logger.info("Preparing housekeeping notification for task #%d, room %s", task_id, room_number)

        settings = await self.settings_service.get_telegram_settings()
        general_settings = await self.settings_service.get_general_settings()

        if not settings.housekeeping_chat_id:
            logger.warning("Housekeeping chat ID not configured")
            return False

        # Use frontend domain from settings if not provided
        if frontend_url is None:
            frontend_url = general_settings.frontend_domain

        # Use public task detail page (no login required)
        task_url = f"{frontend_url}/public/housekeeping/tasks/{task_id}"

        message = (
            f"🧹 <b>มีงานทำความสะอาดใหม่</b>\n"
            f"{'='*40}\n\n"
            f"🏨 <b>ห้อง:</b> {room_number}\n"
            f"🛏️ <b>ประเภท:</b> {room_type}\n"
            f"📋 <b>ID งาน:</b> {task_id}\n\n"
            f"{'='*40}\n"
            f"<a href=\"{task_url}\"><b>👉 คลิกที่นี่เพื่อดูรายละเอียดและรับงาน 👈</b></a>"
        )

        return await self.send_message(settings.housekeeping_chat_id, message)

    async def send_maintenance_notification(
        self,
        task_id: int,
        title: str,
        room_number: str,
        category: str,
        priority: str,
        frontend_url: str = None
    ):
        """Send notification for new maintenance task"""
        logger.info("Preparing maintenance notification for task #%d: %s", task_id, title)

        settings = await self.settings_service.get_telegram_settings()
        general_settings = await self.settings_service.get_general_settings()

        if not settings.maintenance_chat_id:
            logger.warning("Maintenance chat ID not configured")
            return False

        # Use frontend domain from settings if not provided
        if frontend_url is None:
            frontend_url = general_settings.frontend_domain

        # Use public task detail page (no login required)
        task_url = f"{frontend_url}/public/maintenance/tasks/{task_id}"

        priority_emoji = {
            "urgent": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(priority, "⚪")

        message = (
            f"🔧 <b>มีงานซ่อมบำรุงใหม่</b>\n"
            f"{'='*40}\n\n"
            f"<b>📝 {title}</b>\n"
            f"🏨 <b>ห้อง:</b> {room_number}\n"
            f"🔖 <b>ประเภท:</b> {category}\n"
            f"{priority_emoji} <b>สำคัญ:</b> {priority}\n"
            f"📋 <b>ID งาน:</b> {task_id}\n\n"
            f"{'='*40}\n"
            f"<a href=\"{task_url}\"><b>👉 คลิกที่นี่เพื่อดูรายละเอียดและรับงาน 👈</b></a>"
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

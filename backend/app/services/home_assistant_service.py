"""
Home Assistant Service Layer

Handles communication with Home Assistant REST API for breaker control.
"""
import aiohttp
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from app.models.home_assistant import HomeAssistantConfig
from app.core.encryption import encrypt_value, decrypt_value
from app.core.exceptions import (
    HomeAssistantNotConfiguredError,
    HomeAssistantConnectionError,
    HomeAssistantAuthError,
    HomeAssistantTimeoutError,
    HomeAssistantAPIError,
    DecryptionError
)


class HomeAssistantService:
    """
    Service for Home Assistant API communication.

    Handles:
    - Configuration loading from database
    - Connection testing
    - Entity state queries
    - Device control (turn on/off)
    - Health checks
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize Home Assistant service.

        Args:
            db: Database session for loading configuration
        """
        self.db = db
        self.base_url: Optional[str] = None
        self.access_token: Optional[str] = None
        self.headers: Optional[Dict[str, str]] = None
        self._config_loaded = False

    async def _load_config(self) -> HomeAssistantConfig:
        """
        Load Home Assistant configuration from database.

        Returns:
            HomeAssistantConfig: The active configuration

        Raises:
            HomeAssistantNotConfiguredError: If no active config exists
            DecryptionError: If token decryption fails
        """
        result = await self.db.execute(
            select(HomeAssistantConfig)
            .where(HomeAssistantConfig.is_active == True)
            .limit(1)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HomeAssistantNotConfiguredError("Home Assistant ยังไม่ได้ตั้งค่า กรุณาตั้งค่าที่หน้า Settings")

        try:
            # Decrypt token
            self.access_token = decrypt_value(config.access_token)
            self.base_url = config.base_url.rstrip('/')
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            self._config_loaded = True
            return config
        except Exception as e:
            raise DecryptionError(f"ไม่สามารถถอดรหัส Access Token ได้: {str(e)}")

    async def _ensure_config_loaded(self):
        """Ensure configuration is loaded before making API calls"""
        if not self._config_loaded:
            await self._load_config()

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Home Assistant.

        Returns:
            Dict with connection status, version, and response time

        Raises:
            HomeAssistantConnectionError: If connection fails
            HomeAssistantAuthError: If authentication fails
            HomeAssistantTimeoutError: If request times out
        """
        await self._ensure_config_loaded()

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time_ms = int((time.time() - start_time) * 1000)

                    if response.status == 401:
                        raise HomeAssistantAuthError("Access Token ไม่ถูกต้อง")

                    if response.status != 200:
                        raise HomeAssistantAPIError(f"Home Assistant API error (status {response.status})")

                    data = await response.json()

                    return {
                        "success": True,
                        "message": "เชื่อมต่อ Home Assistant สำเร็จ",
                        "ha_version": data.get("version", "unknown"),
                        "response_time_ms": response_time_ms
                    }

        except asyncio.TimeoutError:
            raise HomeAssistantTimeoutError("Home Assistant ไม่ตอบกลับภายใน 10 วินาที")
        except aiohttp.ClientError as e:
            raise HomeAssistantConnectionError(f"ไม่สามารถเชื่อมต่อ Home Assistant ได้: {str(e)}")

    async def test_connection_with_config(
        self,
        base_url: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Test connection with provided credentials (without saving).

        Args:
            base_url: Home Assistant URL to test
            access_token: Access token to test

        Returns:
            Dict with connection status, version, entity count, and response time

        Raises:
            HomeAssistantConnectionError: If connection fails
            HomeAssistantAuthError: If authentication fails
            HomeAssistantTimeoutError: If request times out
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        base_url = base_url.rstrip('/')
        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                # Test basic connection
                async with session.get(
                    f"{base_url}/api/",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 401:
                        raise HomeAssistantAuthError("Access Token ไม่ถูกต้อง")

                    if response.status != 200:
                        raise HomeAssistantAPIError(f"Home Assistant API error (status {response.status})")

                    data = await response.json()
                    ha_version = data.get("version", "unknown")

                # Get entity count
                async with session.get(
                    f"{base_url}/api/states",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        entities = await response.json()
                        entity_count = len(entities)
                    else:
                        entity_count = 0

                response_time_ms = int((time.time() - start_time) * 1000)

                return {
                    "success": True,
                    "message": "เชื่อมต่อ Home Assistant สำเร็จ",
                    "ha_version": ha_version,
                    "entity_count": entity_count,
                    "response_time_ms": response_time_ms
                }

        except asyncio.TimeoutError:
            raise HomeAssistantTimeoutError("Home Assistant ไม่ตอบกลับภายใน 10 วินาที")
        except aiohttp.ClientError as e:
            raise HomeAssistantConnectionError(f"ไม่สามารถเชื่อมต่อ Home Assistant ได้: {str(e)}")

    async def get_entity_state(self, entity_id: str) -> Dict[str, Any]:
        """
        Get current state of an entity.

        Args:
            entity_id: Entity ID (e.g., "switch.room_101_breaker")

        Returns:
            Dict with entity state and attributes

        Raises:
            HomeAssistantAPIError: If API call fails
        """
        await self._ensure_config_loaded()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/states/{entity_id}",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 404:
                        return {
                            "entity_id": entity_id,
                            "state": "unavailable",
                            "attributes": {},
                            "available": False
                        }

                    if response.status != 200:
                        raise HomeAssistantAPIError(f"Failed to get entity state (status {response.status})")

                    data = await response.json()

                    return {
                        "entity_id": data.get("entity_id"),
                        "state": data.get("state"),
                        "attributes": data.get("attributes", {}),
                        "available": True,
                        "last_changed": data.get("last_changed"),
                        "last_updated": data.get("last_updated")
                    }

        except asyncio.TimeoutError:
            raise HomeAssistantTimeoutError(f"Timeout getting state for {entity_id}")
        except aiohttp.ClientError as e:
            raise HomeAssistantConnectionError(f"Connection error: {str(e)}")

    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str,
        retry_count: int = 0,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Call a Home Assistant service (e.g., turn_on, turn_off).

        Args:
            domain: Service domain (e.g., "switch")
            service: Service name (e.g., "turn_on", "turn_off")
            entity_id: Target entity ID
            retry_count: Current retry attempt
            max_retries: Maximum retry attempts

        Returns:
            Dict with success status and response time

        Raises:
            HomeAssistantAPIError: If service call fails after retries
        """
        await self._ensure_config_loaded()

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/services/{domain}/{service}",
                    headers=self.headers,
                    json={"entity_id": entity_id},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_time_ms = int((time.time() - start_time) * 1000)

                    if response.status in [200, 201]:
                        return {
                            "success": True,
                            "response_time_ms": response_time_ms,
                            "retry_count": retry_count
                        }
                    else:
                        # Retry on failure
                        if retry_count < max_retries:
                            await asyncio.sleep(1 * (retry_count + 1))  # Exponential backoff
                            return await self.call_service(
                                domain, service, entity_id,
                                retry_count + 1, max_retries
                            )
                        else:
                            raise HomeAssistantAPIError(
                                f"Service call failed after {max_retries} retries (status {response.status})"
                            )

        except asyncio.TimeoutError:
            if retry_count < max_retries:
                await asyncio.sleep(1 * (retry_count + 1))
                return await self.call_service(
                    domain, service, entity_id,
                    retry_count + 1, max_retries
                )
            else:
                raise HomeAssistantTimeoutError(f"Service call timeout after {max_retries} retries")
        except aiohttp.ClientError as e:
            if retry_count < max_retries:
                await asyncio.sleep(1 * (retry_count + 1))
                return await self.call_service(
                    domain, service, entity_id,
                    retry_count + 1, max_retries
                )
            else:
                raise HomeAssistantConnectionError(f"Connection error after {max_retries} retries: {str(e)}")

    async def turn_on(self, entity_id: str) -> Dict[str, Any]:
        """
        Turn on a switch/light entity.

        Args:
            entity_id: Entity ID to turn on

        Returns:
            Dict with success status and response time
        """
        domain = entity_id.split('.')[0]  # Extract domain (e.g., "switch" from "switch.room_101")
        return await self.call_service(domain, "turn_on", entity_id)

    async def turn_off(self, entity_id: str) -> Dict[str, Any]:
        """
        Turn off a switch/light entity.

        Args:
            entity_id: Entity ID to turn off

        Returns:
            Dict with success status and response time
        """
        domain = entity_id.split('.')[0]
        return await self.call_service(domain, "turn_off", entity_id)

    async def get_all_entities(self, domain_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all entities from Home Assistant.

        Args:
            domain_filter: Optional domain to filter (e.g., "switch")

        Returns:
            List of entity dictionaries
        """
        await self._ensure_config_loaded()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/states",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        raise HomeAssistantAPIError(f"Failed to get entities (status {response.status})")

                    entities = await response.json()

                    # Filter by domain if specified
                    if domain_filter:
                        entities = [
                            e for e in entities
                            if e.get("entity_id", "").startswith(f"{domain_filter}.")
                        ]

                    return [
                        {
                            "entity_id": e.get("entity_id"),
                            "friendly_name": e.get("attributes", {}).get("friendly_name", e.get("entity_id")),
                            "state": e.get("state"),
                            "attributes": e.get("attributes", {})
                        }
                        for e in entities
                    ]

        except asyncio.TimeoutError:
            raise HomeAssistantTimeoutError("Timeout getting entities")
        except aiohttp.ClientError as e:
            raise HomeAssistantConnectionError(f"Connection error: {str(e)}")

    async def update_config_status(self, is_online: bool, ha_version: Optional[str] = None):
        """
        Update configuration status in database.

        Args:
            is_online: Whether Home Assistant is online
            ha_version: Home Assistant version (optional)
        """
        config = await self._load_config()
        config.is_online = is_online
        config.last_ping_at = datetime.now()
        if ha_version:
            config.ha_version = ha_version

        await self.db.commit()

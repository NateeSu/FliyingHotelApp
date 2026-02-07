"""
Home Assistant Configuration API Endpoints

Manages Home Assistant connection settings and configuration.
ADMIN-only access for configuration management.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

logger = logging.getLogger(__name__)

from app.core.dependencies import get_db, require_role, get_current_user_id
from app.services.home_assistant_service import HomeAssistantService
from app.models.home_assistant import HomeAssistantConfig
from app.schemas.home_assistant import (
    HomeAssistantConfigCreate,
    HomeAssistantConfigUpdate,
    HomeAssistantConfigResponse,
    HomeAssistantTestConnectionRequest,
    HomeAssistantTestConnectionResponse,
    HomeAssistantStatusResponse,
    HomeAssistantEntitiesResponse,
    HomeAssistantEntityResponse
)
from app.core.encryption import encrypt_value, mask_token
from app.core.exceptions import HomeAssistantNotConfiguredError
from sqlalchemy import select

router = APIRouter()


@router.get("/config", response_model=HomeAssistantConfigResponse)
async def get_home_assistant_config(
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    ดึงข้อมูลการตั้งค่า Home Assistant ปัจจุบัน

    **สิทธิ์**: ADMIN เท่านั้น

    **Returns**:
    - Configuration ปัจจุบัน (access_token จะถูก mask)
    """
    result = await db.execute(
        select(HomeAssistantConfig)
        .where(HomeAssistantConfig.is_active == True)
        .limit(1)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HomeAssistantNotConfiguredError("ยังไม่ได้ตั้งค่า Home Assistant")

    # Mask the access token for security
    from app.core.encryption import decrypt_value
    try:
        decrypted_token = decrypt_value(config.access_token)
        masked_token = mask_token(decrypted_token)
    except:
        masked_token = "***"

    return HomeAssistantConfigResponse(
        id=config.id,
        base_url=config.base_url,
        access_token_masked=masked_token,
        is_online=config.is_online,
        last_ping_at=config.last_ping_at,
        ha_version=config.ha_version,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at
    )


@router.post("/config", response_model=HomeAssistantConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_home_assistant_config(
    data: HomeAssistantConfigCreate,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    สร้างหรืออัปเดตการตั้งค่า Home Assistant

    **สิทธิ์**: ADMIN เท่านั้น

    **Body Parameters**:
    - **base_url**: URL ของ Home Assistant (เช่น http://192.168.1.100:8123)
    - **access_token**: Long-Lived Access Token จาก Home Assistant

    **Returns**:
    - Configuration ที่สร้าง/อัปเดต

    **Note**: ระบบจะทดสอบการเชื่อมต่อก่อน และ encrypt token ก่อนบันทึก
    """
    # Test connection first
    ha_service = HomeAssistantService(db)
    try:
        test_result = await ha_service.test_connection_with_config(
            data.base_url,
            data.access_token
        )
    except Exception as e:
        error_detail = getattr(e, 'detail', None) or str(e) or type(e).__name__
        logger.error(f"HA config save - connection test failed: {type(e).__name__}: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ไม่สามารถเชื่อมต่อ Home Assistant ได้: {error_detail}"
        )

    # Encrypt the access token
    encrypted_token = encrypt_value(data.access_token)

    # Check if config already exists
    result = await db.execute(
        select(HomeAssistantConfig).where(HomeAssistantConfig.is_active == True)
    )
    existing_config = result.scalar_one_or_none()

    if existing_config:
        # Update existing
        existing_config.base_url = data.base_url
        existing_config.access_token = encrypted_token
        existing_config.is_online = True
        existing_config.ha_version = test_result.get("ha_version")
        config = existing_config
    else:
        # Create new
        config = HomeAssistantConfig(
            base_url=data.base_url,
            access_token=encrypted_token,
            is_online=True,
            ha_version=test_result.get("ha_version")
        )
        db.add(config)

    await db.commit()
    await db.refresh(config)

    masked_token = mask_token(data.access_token)

    return HomeAssistantConfigResponse(
        id=config.id,
        base_url=config.base_url,
        access_token_masked=masked_token,
        is_online=config.is_online,
        last_ping_at=config.last_ping_at,
        ha_version=config.ha_version,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at
    )


@router.put("/config", response_model=HomeAssistantConfigResponse)
async def update_home_assistant_config(
    data: HomeAssistantConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    อัปเดตการตั้งค่า Home Assistant บางส่วน

    **สิทธิ์**: ADMIN เท่านั้น

    **Body Parameters**:
    - **base_url**: URL ใหม่ (ถ้าต้องการเปลี่ยน)
    - **access_token**: Token ใหม่ (ถ้าต้องการเปลี่ยน)

    **Returns**:
    - Configuration ที่อัปเดต
    """
    result = await db.execute(
        select(HomeAssistantConfig).where(HomeAssistantConfig.is_active == True)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HomeAssistantNotConfiguredError("ยังไม่ได้ตั้งค่า Home Assistant")

    # Prepare new values for testing
    test_url = data.base_url if data.base_url else config.base_url

    if data.access_token:
        test_token = data.access_token
    else:
        # Decrypt existing token for testing
        from app.core.encryption import decrypt_value
        test_token = decrypt_value(config.access_token)

    # Test connection with new values
    ha_service = HomeAssistantService(db)
    try:
        test_result = await ha_service.test_connection_with_config(test_url, test_token)
    except Exception as e:
        error_detail = getattr(e, 'detail', None) or str(e) or type(e).__name__
        logger.error(f"HA config update - connection test failed: {type(e).__name__}: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ไม่สามารถเชื่อมต่อด้วยค่าใหม่ได้: {error_detail}"
        )

    # Update config
    if data.base_url:
        config.base_url = data.base_url
    if data.access_token:
        config.access_token = encrypt_value(data.access_token)

    config.is_online = True
    config.ha_version = test_result.get("ha_version")

    await db.commit()
    await db.refresh(config)

    masked_token = mask_token(test_token)

    return HomeAssistantConfigResponse(
        id=config.id,
        base_url=config.base_url,
        access_token_masked=masked_token,
        is_online=config.is_online,
        last_ping_at=config.last_ping_at,
        ha_version=config.ha_version,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at
    )


@router.delete("/config", status_code=status.HTTP_204_NO_CONTENT)
async def delete_home_assistant_config(
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    ลบการตั้งค่า Home Assistant (soft delete)

    **สิทธิ์**: ADMIN เท่านั้น

    **Returns**: HTTP 204 No Content
    """
    result = await db.execute(
        select(HomeAssistantConfig).where(HomeAssistantConfig.is_active == True)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HomeAssistantNotConfiguredError("ยังไม่ได้ตั้งค่า Home Assistant")

    config.is_active = False
    await db.commit()

    return None


@router.post("/test-connection", response_model=HomeAssistantTestConnectionResponse)
async def test_home_assistant_connection(
    data: HomeAssistantTestConnectionRequest,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    ทดสอบการเชื่อมต่อ Home Assistant โดยไม่บันทึกลง database

    **สิทธิ์**: ADMIN เท่านั้น

    **Body Parameters**:
    - **base_url**: URL ที่ต้องการทดสอบ
    - **access_token**: Token ที่ต้องการทดสอบ

    **Returns**:
    - ผลการทดสอบ (success, version, entity_count, response_time)
    """
    ha_service = HomeAssistantService(db)

    try:
        result = await ha_service.test_connection_with_config(
            data.base_url,
            data.access_token
        )

        return HomeAssistantTestConnectionResponse(
            success=result["success"],
            message=result["message"],
            ha_version=result.get("ha_version"),
            entity_count=result.get("entity_count"),
            response_time_ms=result.get("response_time_ms")
        )
    except Exception as e:
        error_detail = getattr(e, 'detail', None) or str(e) or type(e).__name__
        logger.error(f"HA test connection failed: {type(e).__name__}: {error_detail}")
        return HomeAssistantTestConnectionResponse(
            success=False,
            message=f"การเชื่อมต่อล้มเหลว: {error_detail}",
            ha_version=None,
            entity_count=None,
            response_time_ms=None
        )


@router.get("/status", response_model=HomeAssistantStatusResponse)
async def get_home_assistant_status(
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ตรวจสอบสถานะการเชื่อมต่อ Home Assistant

    **สิทธิ์**: ทุก role ที่ login แล้ว

    **Returns**:
    - สถานะการเชื่อมต่อปัจจุบัน
    """
    result = await db.execute(
        select(HomeAssistantConfig).where(HomeAssistantConfig.is_active == True)
    )
    config = result.scalar_one_or_none()

    if not config:
        return HomeAssistantStatusResponse(
            is_configured=False,
            is_online=False,
            last_ping_at=None,
            ha_version=None,
            base_url=None
        )

    return HomeAssistantStatusResponse(
        is_configured=True,
        is_online=config.is_online,
        last_ping_at=config.last_ping_at,
        ha_version=config.ha_version,
        base_url=config.base_url
    )


@router.get("/entities", response_model=HomeAssistantEntitiesResponse)
async def get_home_assistant_entities(
    domain_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    ดึงรายการ entities ทั้งหมดจาก Home Assistant

    **สิทธิ์**: ADMIN เท่านั้น

    **Query Parameters**:
    - **domain_filter**: กรองตาม domain (เช่น switch, light)

    **Returns**:
    - รายการ entities และจำนวนทั้งหมด

    **Use Case**: ใช้สำหรับเลือก entity_id ตอนสร้าง breaker ใหม่
    """
    ha_service = HomeAssistantService(db)

    try:
        entities_data = await ha_service.get_all_entities(domain_filter=domain_filter)

        entities = [
            HomeAssistantEntityResponse(
                entity_id=e["entity_id"],
                friendly_name=e.get("friendly_name"),
                state=e.get("state"),
                attributes=e.get("attributes")
            )
            for e in entities_data
        ]

        return HomeAssistantEntitiesResponse(
            entities=entities,
            total=len(entities)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ไม่สามารถดึงรายการ entities ได้: {str(e)}"
        )

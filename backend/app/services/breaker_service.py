"""
Breaker Service Layer

Manages breaker devices, control logic, and activity logging.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import asyncio

from app.models.home_assistant import (
    HomeAssistantBreaker,
    BreakerActivityLog,
    BreakerControlQueue,
    BreakerState,
    BreakerAction,
    TriggerType,
    ActionStatus,
    QueueStatus,
    TargetState
)
from app.models.room import Room, RoomStatus
from app.models.user import User
from app.services.home_assistant_service import HomeAssistantService
from app.core.exceptions import (
    BreakerNotFoundError,
    BreakerUnavailableError,
    BreakerControlError,
    BreakerAlreadyExistsError,
    BreakerRoomConflictError,
    HomeAssistantException
)


class BreakerService:
    """
    Service for breaker management and control.

    Handles:
    - CRUD operations for breakers
    - Manual control (turn on/off)
    - Automatic control based on room status
    - State synchronization
    - Activity logging
    - Control queue management
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize breaker service.

        Args:
            db: Database session
        """
        self.db = db
        self.ha_service = HomeAssistantService(db)

    # ========================================================================
    # CRUD Operations
    # ========================================================================

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        room_id: Optional[int] = None,
        auto_control_enabled: Optional[bool] = None,
        current_state: Optional[BreakerState] = None,
        is_active: Optional[bool] = True
    ) -> List[HomeAssistantBreaker]:
        """Get all breakers with optional filtering"""
        query = select(HomeAssistantBreaker).options(
            selectinload(HomeAssistantBreaker.room)
        )

        conditions = []
        if room_id is not None:
            conditions.append(HomeAssistantBreaker.room_id == room_id)
        if auto_control_enabled is not None:
            conditions.append(HomeAssistantBreaker.auto_control_enabled == auto_control_enabled)
        if current_state is not None:
            conditions.append(HomeAssistantBreaker.current_state == current_state)
        if is_active is not None:
            conditions.append(HomeAssistantBreaker.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit).order_by(HomeAssistantBreaker.id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, breaker_id: int) -> Optional[HomeAssistantBreaker]:
        """Get breaker by ID with room relationship"""
        result = await self.db.execute(
            select(HomeAssistantBreaker)
            .options(selectinload(HomeAssistantBreaker.room))
            .where(HomeAssistantBreaker.id == breaker_id)
        )
        return result.scalar_one_or_none()

    async def get_by_entity_id(self, entity_id: str) -> Optional[HomeAssistantBreaker]:
        """Get breaker by entity ID"""
        result = await self.db.execute(
            select(HomeAssistantBreaker)
            .where(HomeAssistantBreaker.entity_id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_by_room_id(self, room_id: int) -> Optional[HomeAssistantBreaker]:
        """Get breaker by room ID"""
        result = await self.db.execute(
            select(HomeAssistantBreaker)
            .where(HomeAssistantBreaker.room_id == room_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        entity_id: str,
        friendly_name: str,
        room_id: Optional[int] = None,
        auto_control_enabled: bool = True
    ) -> HomeAssistantBreaker:
        """
        Create a new breaker.

        Args:
            entity_id: Home Assistant entity ID
            friendly_name: Human-readable name
            room_id: Optional room to link
            auto_control_enabled: Enable automatic control

        Returns:
            Created breaker

        Raises:
            BreakerAlreadyExistsError: If entity_id already exists (and is active)
            BreakerRoomConflictError: If room already has a breaker
        """
        # Check if entity_id already exists
        existing = await self.get_by_entity_id(entity_id)
        if existing:
            # If the breaker was soft-deleted, reactivate it
            if not existing.is_active:
                # Reactivate the soft-deleted breaker with new settings
                existing.friendly_name = friendly_name
                existing.room_id = room_id
                existing.auto_control_enabled = auto_control_enabled
                existing.is_active = True
                existing.current_state = BreakerState.UNAVAILABLE
                existing.is_available = False
                existing.consecutive_errors = 0
                existing.last_error_message = None

                await self.db.commit()

                # Reload with relationships first
                result = await self.get_by_id(existing.id)

                # Sync initial state from Home Assistant (non-blocking, best-effort)
                try:
                    import asyncio
                    # Use asyncio.wait_for with 3 second timeout to avoid blocking
                    await asyncio.wait_for(self.sync_breaker_state(existing.id), timeout=3.0)
                except asyncio.TimeoutError:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Timeout syncing breaker {existing.id} state during reactivation (HA may be offline)")
                except Exception as e:
                    # Ignore if HA is not available during creation
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to sync breaker {existing.id} state during reactivation: {e}")

                return result
            else:
                # Breaker is active, cannot create duplicate
                raise BreakerAlreadyExistsError(f"Breaker {entity_id} มีอยู่แล้วในระบบ")

        # Check if room already has a breaker
        if room_id:
            existing_room_breaker = await self.get_by_room_id(room_id)
            if existing_room_breaker and existing_room_breaker.is_active:
                raise BreakerRoomConflictError(f"ห้องนี้มี breaker ({existing_room_breaker.entity_id}) กำหนดอยู่แล้ว")

        # Create breaker
        breaker = HomeAssistantBreaker(
            entity_id=entity_id,
            friendly_name=friendly_name,
            room_id=room_id,
            auto_control_enabled=auto_control_enabled,
            current_state=BreakerState.UNAVAILABLE,
            is_available=False
        )

        self.db.add(breaker)
        await self.db.commit()

        # Reload with relationships first
        result = await self.get_by_id(breaker.id)

        # Sync initial state from Home Assistant (non-blocking, best-effort)
        try:
            import asyncio
            # Use asyncio.wait_for with 3 second timeout to avoid blocking
            await asyncio.wait_for(self.sync_breaker_state(breaker.id), timeout=3.0)
        except asyncio.TimeoutError:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Timeout syncing breaker {breaker.id} state during creation (HA may be offline)")
        except Exception as e:
            # Ignore if HA is not available during creation
            # Log error but don't fail the creation
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to sync breaker {breaker.id} state during creation: {e}")

        return result

    async def update(
        self,
        breaker_id: int,
        entity_id: Optional[str] = None,
        friendly_name: Optional[str] = None,
        room_id: Optional[int] = None,
        auto_control_enabled: Optional[bool] = None
    ) -> HomeAssistantBreaker:
        """Update breaker information"""
        breaker = await self.get_by_id(breaker_id)
        if not breaker:
            raise BreakerNotFoundError()

        # Check entity_id uniqueness (only among active breakers)
        if entity_id and entity_id != breaker.entity_id:
            existing = await self.get_by_entity_id(entity_id)
            if existing and existing.is_active:
                raise BreakerAlreadyExistsError(f"Entity ID {entity_id} มีอยู่แล้ว")
            breaker.entity_id = entity_id

        # Check room uniqueness (only among active breakers)
        if room_id is not None and room_id != breaker.room_id:
            existing_room_breaker = await self.get_by_room_id(room_id)
            if existing_room_breaker and existing_room_breaker.is_active and existing_room_breaker.id != breaker_id:
                raise BreakerRoomConflictError(f"ห้องนี้มี breaker กำหนดอยู่แล้ว")
            breaker.room_id = room_id

        if friendly_name is not None:
            breaker.friendly_name = friendly_name
        if auto_control_enabled is not None:
            breaker.auto_control_enabled = auto_control_enabled

        await self.db.commit()
        await self.db.refresh(breaker)
        return breaker

    async def delete(self, breaker_id: int) -> bool:
        """Soft delete breaker"""
        breaker = await self.get_by_id(breaker_id)
        if not breaker:
            raise BreakerNotFoundError()

        breaker.is_active = False
        await self.db.commit()
        return True

    # ========================================================================
    # Control Operations
    # ========================================================================

    async def turn_on(
        self,
        breaker_id: int,
        trigger_type: TriggerType = TriggerType.MANUAL,
        triggered_by: Optional[int] = None,
        room_status_before: Optional[str] = None,
        room_status_after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Turn on breaker.

        Args:
            breaker_id: Breaker ID
            trigger_type: How action was triggered
            triggered_by: User ID who triggered (for MANUAL)
            room_status_before: Room status before action
            room_status_after: Room status after action

        Returns:
            Dict with success status and details
        """
        breaker = await self.get_by_id(breaker_id)
        if not breaker:
            raise BreakerNotFoundError()

        if not breaker.is_available:
            raise BreakerUnavailableError(f"Breaker {breaker.entity_id} ไม่พร้อมใช้งานใน Home Assistant")

        start_time = datetime.now()
        action_status = ActionStatus.FAILED
        error_message = None
        response_time_ms = None

        try:
            # Call Home Assistant API
            result = await self.ha_service.turn_on(breaker.entity_id)
            action_status = ActionStatus.SUCCESS
            response_time_ms = result.get("response_time_ms")

            # Update breaker state
            breaker.current_state = BreakerState.ON
            breaker.last_state_update = datetime.now()
            breaker.consecutive_errors = 0
            breaker.last_error_message = None

        except Exception as e:
            error_message = str(e)
            breaker.consecutive_errors += 1
            breaker.last_error_message = error_message
            response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Log activity
        await self._log_activity(
            breaker_id=breaker_id,
            action=BreakerAction.TURN_ON,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            room_status_before=room_status_before,
            room_status_after=room_status_after,
            status=action_status,
            error_message=error_message,
            response_time_ms=response_time_ms
        )

        await self.db.commit()

        if action_status == ActionStatus.FAILED:
            # Broadcast error event
            from app.core.websocket import websocket_manager
            await websocket_manager.broadcast_breaker_error(
                breaker_id=breaker_id,
                entity_id=breaker.entity_id,
                error_message=error_message,
                consecutive_errors=breaker.consecutive_errors,
                room_id=breaker.room_id
            )
            raise BreakerControlError(f"ไม่สามารถเปิด breaker ได้: {error_message}")

        # Broadcast control event
        from app.core.websocket import websocket_manager
        await websocket_manager.broadcast_breaker_control(
            breaker_id=breaker_id,
            action="TURN_ON",
            status="SUCCESS",
            room_id=breaker.room_id,
            room_number=breaker.room.room_number if breaker.room else None,
            trigger_type=trigger_type.value
        )

        return {
            "success": True,
            "message": f"เปิด breaker {breaker.friendly_name} สำเร็จ",
            "breaker_id": breaker_id,
            "new_state": BreakerState.ON,
            "response_time_ms": response_time_ms
        }

    async def turn_off(
        self,
        breaker_id: int,
        trigger_type: TriggerType = TriggerType.MANUAL,
        triggered_by: Optional[int] = None,
        room_status_before: Optional[str] = None,
        room_status_after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Turn off breaker (similar to turn_on)"""
        breaker = await self.get_by_id(breaker_id)
        if not breaker:
            raise BreakerNotFoundError()

        if not breaker.is_available:
            raise BreakerUnavailableError(f"Breaker {breaker.entity_id} ไม่พร้อมใช้งานใน Home Assistant")

        start_time = datetime.now()
        action_status = ActionStatus.FAILED
        error_message = None
        response_time_ms = None

        try:
            result = await self.ha_service.turn_off(breaker.entity_id)
            action_status = ActionStatus.SUCCESS
            response_time_ms = result.get("response_time_ms")

            breaker.current_state = BreakerState.OFF
            breaker.last_state_update = datetime.now()
            breaker.consecutive_errors = 0
            breaker.last_error_message = None

        except Exception as e:
            error_message = str(e)
            breaker.consecutive_errors += 1
            breaker.last_error_message = error_message
            response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        await self._log_activity(
            breaker_id=breaker_id,
            action=BreakerAction.TURN_OFF,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            room_status_before=room_status_before,
            room_status_after=room_status_after,
            status=action_status,
            error_message=error_message,
            response_time_ms=response_time_ms
        )

        await self.db.commit()

        if action_status == ActionStatus.FAILED:
            # Broadcast error event
            from app.core.websocket import websocket_manager
            await websocket_manager.broadcast_breaker_error(
                breaker_id=breaker_id,
                entity_id=breaker.entity_id,
                error_message=error_message,
                consecutive_errors=breaker.consecutive_errors,
                room_id=breaker.room_id
            )
            raise BreakerControlError(f"ไม่สามารถปิด breaker ได้: {error_message}")

        # Broadcast control event
        from app.core.websocket import websocket_manager
        await websocket_manager.broadcast_breaker_control(
            breaker_id=breaker_id,
            action="TURN_OFF",
            status="SUCCESS",
            room_id=breaker.room_id,
            room_number=breaker.room.room_number if breaker.room else None,
            trigger_type=trigger_type.value
        )

        return {
            "success": True,
            "message": f"ปิด breaker {breaker.friendly_name} สำเร็จ",
            "breaker_id": breaker_id,
            "new_state": BreakerState.OFF,
            "response_time_ms": response_time_ms
        }

    async def sync_breaker_state(self, breaker_id: int) -> Dict[str, Any]:
        """
        Sync breaker state from Home Assistant.

        Args:
            breaker_id: Breaker ID

        Returns:
            Dict with current state and availability
        """
        breaker = await self.get_by_id(breaker_id)
        if not breaker:
            raise BreakerNotFoundError()

        try:
            state_data = await self.ha_service.get_entity_state(breaker.entity_id)

            # Update breaker
            ha_state = state_data.get("state", "unavailable").lower()
            breaker.is_available = state_data.get("available", False)
            breaker.ha_attributes = state_data.get("attributes", {})
            breaker.last_state_update = datetime.now(ZoneInfo("Asia/Bangkok"))

            # Map HA state to BreakerState
            if ha_state == "on":
                breaker.current_state = BreakerState.ON
            elif ha_state == "off":
                breaker.current_state = BreakerState.OFF
            else:
                breaker.current_state = BreakerState.UNAVAILABLE

            # Clear error info on successful sync
            breaker.consecutive_errors = 0
            breaker.last_error_message = None

            # Log sync activity
            await self._log_activity(
                breaker_id=breaker_id,
                action=BreakerAction.STATUS_SYNC,
                trigger_type=TriggerType.SYSTEM,
                status=ActionStatus.SUCCESS
            )

            await self.db.commit()

            return {
                "success": True,
                "message": "ซิงค์สถานะสำเร็จ",
                "breaker_id": breaker_id,
                "current_state": breaker.current_state,
                "is_available": breaker.is_available,
                "synced_at": breaker.last_state_update,
                "consecutive_errors": breaker.consecutive_errors,
                "last_error_message": breaker.last_error_message
            }

        except Exception as e:
            # Log failed sync
            await self._log_activity(
                breaker_id=breaker_id,
                action=BreakerAction.STATUS_SYNC,
                trigger_type=TriggerType.SYSTEM,
                status=ActionStatus.FAILED,
                error_message=str(e)
            )

            # Update breaker error info
            breaker.consecutive_errors += 1
            breaker.last_error_message = str(e)

            await self.db.commit()

            # Return failure result instead of raising
            return {
                "success": False,
                "message": f"ซิงค์สถานะไม่สำเร็จ: {str(e)}",
                "breaker_id": breaker_id,
                "current_state": breaker.current_state,
                "is_available": breaker.is_available,
                "synced_at": breaker.last_state_update,
                "consecutive_errors": breaker.consecutive_errors,
                "last_error_message": breaker.last_error_message
            }

    async def sync_all_breakers(self) -> Dict[str, Any]:
        """Sync all active breakers"""
        breakers = await self.get_all(is_active=True)
        success_count = 0
        failed_count = 0

        for breaker in breakers:
            try:
                await self.sync_breaker_state(breaker.id)
                success_count += 1
            except Exception:
                failed_count += 1

        return {
            "success": True,
            "message": f"ซิงค์เสร็จสิ้น: สำเร็จ {success_count}, ล้มเหลว {failed_count}",
            "total": len(breakers),
            "success_count": success_count,
            "failed_count": failed_count
        }

    # ========================================================================
    # Auto Control Logic
    # ========================================================================

    async def auto_control_on_room_status_change(
        self,
        room_id: int,
        old_status: RoomStatus,
        new_status: RoomStatus
    ):
        """
        Automatically control breaker based on room status change.

        Business Logic:
        - Turn ON if new_status is OCCUPIED or CLEANING
        - Turn OFF if new_status is AVAILABLE, RESERVED, or OUT_OF_SERVICE

        Args:
            room_id: Room ID
            old_status: Previous room status
            new_status: New room status
        """
        breaker = await self.get_by_room_id(room_id)

        if not breaker:
            return  # No breaker assigned to this room

        if not breaker.auto_control_enabled:
            return  # Auto control disabled

        # Determine target state
        target_state = None
        if new_status in [RoomStatus.OCCUPIED, RoomStatus.CLEANING]:
            target_state = TargetState.ON
        elif new_status in [RoomStatus.AVAILABLE, RoomStatus.RESERVED, RoomStatus.OUT_OF_SERVICE]:
            target_state = TargetState.OFF

        if target_state:
            # Add to control queue with 3-second debounce
            await self._add_to_control_queue(
                breaker_id=breaker.id,
                target_state=target_state,
                trigger_type=TriggerType.AUTO,
                debounce_seconds=3
            )

    # ========================================================================
    # Activity Logs
    # ========================================================================

    async def get_activity_logs(
        self,
        breaker_id: Optional[int] = None,
        action: Optional[BreakerAction] = None,
        trigger_type: Optional[TriggerType] = None,
        status: Optional[ActionStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[BreakerActivityLog]:
        """Get activity logs with filtering"""
        query = select(BreakerActivityLog).options(
            selectinload(BreakerActivityLog.breaker),
            selectinload(BreakerActivityLog.triggered_by_user)
        )

        conditions = []
        if breaker_id:
            conditions.append(BreakerActivityLog.breaker_id == breaker_id)
        if action:
            conditions.append(BreakerActivityLog.action == action)
        if trigger_type:
            conditions.append(BreakerActivityLog.trigger_type == trigger_type)
        if status:
            conditions.append(BreakerActivityLog.status == status)
        if start_date:
            conditions.append(BreakerActivityLog.created_at >= start_date)
        if end_date:
            conditions.append(BreakerActivityLog.created_at <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(BreakerActivityLog.created_at)).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _log_activity(
        self,
        breaker_id: int,
        action: BreakerAction,
        trigger_type: TriggerType,
        status: ActionStatus,
        triggered_by: Optional[int] = None,
        room_status_before: Optional[str] = None,
        room_status_after: Optional[str] = None,
        error_message: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ):
        """Internal method to log breaker activity"""
        log = BreakerActivityLog(
            breaker_id=breaker_id,
            action=action,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            room_status_before=room_status_before,
            room_status_after=room_status_after,
            status=status,
            error_message=error_message,
            response_time_ms=response_time_ms
        )
        self.db.add(log)

    # ========================================================================
    # Control Queue
    # ========================================================================

    async def _add_to_control_queue(
        self,
        breaker_id: int,
        target_state: TargetState,
        trigger_type: TriggerType,
        triggered_by: Optional[int] = None,
        priority: int = 5,
        debounce_seconds: int = 0
    ):
        """Add command to control queue"""
        scheduled_at = datetime.now()
        if debounce_seconds > 0:
            scheduled_at = scheduled_at + timedelta(seconds=debounce_seconds)

        queue_item = BreakerControlQueue(
            breaker_id=breaker_id,
            target_state=target_state,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            priority=priority,
            scheduled_at=scheduled_at,
            status=QueueStatus.PENDING
        )

        self.db.add(queue_item)
        await self.db.commit()

    # ========================================================================
    # Statistics
    # ========================================================================

    async def get_statistics(self) -> Dict[str, Any]:
        """Get breaker statistics"""
        # Total breakers
        total_result = await self.db.execute(
            select(func.count(HomeAssistantBreaker.id))
            .where(HomeAssistantBreaker.is_active == True)
        )
        total_breakers = total_result.scalar()

        # Online breakers
        online_result = await self.db.execute(
            select(func.count(HomeAssistantBreaker.id))
            .where(and_(
                HomeAssistantBreaker.is_active == True,
                HomeAssistantBreaker.is_available == True
            ))
        )
        online_breakers = online_result.scalar()

        # Breakers ON
        on_result = await self.db.execute(
            select(func.count(HomeAssistantBreaker.id))
            .where(and_(
                HomeAssistantBreaker.is_active == True,
                HomeAssistantBreaker.current_state == BreakerState.ON
            ))
        )
        breakers_on = on_result.scalar()

        # Breakers with auto control
        auto_result = await self.db.execute(
            select(func.count(HomeAssistantBreaker.id))
            .where(and_(
                HomeAssistantBreaker.is_active == True,
                HomeAssistantBreaker.auto_control_enabled == True
            ))
        )
        auto_control_enabled = auto_result.scalar()

        # Today's actions
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        actions_today_result = await self.db.execute(
            select(func.count(BreakerActivityLog.id))
            .where(BreakerActivityLog.created_at >= today_start)
        )
        total_actions_today = actions_today_result.scalar()

        # Success rate today
        success_today_result = await self.db.execute(
            select(func.count(BreakerActivityLog.id))
            .where(and_(
                BreakerActivityLog.created_at >= today_start,
                BreakerActivityLog.status == ActionStatus.SUCCESS
            ))
        )
        success_today = success_today_result.scalar()
        success_rate = (success_today / total_actions_today * 100) if total_actions_today > 0 else 0

        return {
            "total_breakers": total_breakers,
            "online_breakers": online_breakers,
            "offline_breakers": total_breakers - online_breakers,
            "breakers_on": breakers_on,
            "breakers_off": online_breakers - breakers_on,
            "auto_control_enabled": auto_control_enabled,
            "breakers_with_errors": 0,  # TODO: implement error count
            "total_actions_today": total_actions_today,
            "success_rate_today": round(success_rate, 2),
            "avg_response_time_ms": None  # TODO: calculate average
        }

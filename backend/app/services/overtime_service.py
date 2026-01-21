"""
Overtime Service
Handles detection and processing of overtime temporary stays
"""
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
from datetime import datetime

from app.models.check_in import CheckIn, CheckInStatusEnum, StayTypeEnum
from app.models.room import Room, RoomStatus
from app.core.datetime_utils import now_thailand
from app.core.websocket import websocket_manager


class OvertimeService:
    """Service for handling overtime detection and processing"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_and_process_overtime_stays(self) -> Dict[str, Any]:
        """
        Check all TEMPORARY stays and process those that have exceeded 3 hours

        Returns:
            Dict with processing results including:
            - total_checked: Total TEMPORARY stays checked
            - overtime_found: Number of overtime stays found
            - rooms_updated: Number of rooms updated to OCCUPIED_OVERTIME
            - processed_check_ins: List of check-in IDs processed
        """
        now = now_thailand()

        # Find all TEMPORARY stays that are CHECKED_IN and past expected_check_out_time
        stmt = select(CheckIn).options(
            selectinload(CheckIn.room),
            selectinload(CheckIn.customer)
        ).where(
            and_(
                CheckIn.stay_type == StayTypeEnum.TEMPORARY,
                CheckIn.status == CheckInStatusEnum.CHECKED_IN,
                CheckIn.expected_check_out_time <= now,
                CheckIn.is_overtime == 0  # Not already marked as overtime
            )
        )

        result = await self.db.execute(stmt)
        overtime_check_ins = result.scalars().all()

        processed_count = 0
        processed_ids = []

        for check_in in overtime_check_ins:
            try:
                # Calculate overtime duration
                overtime_duration = now - check_in.expected_check_out_time
                overtime_minutes = int(overtime_duration.total_seconds() / 60)

                # Update check_in record
                check_in.is_overtime = 1
                check_in.overtime_minutes = overtime_minutes

                # Get the room
                room = await self.db.get(Room, check_in.room_id)

                if room and room.status == RoomStatus.OCCUPIED:
                    # Update room status to OCCUPIED_OVERTIME
                    old_status = room.status
                    room.status = RoomStatus.OCCUPIED_OVERTIME

                    await self.db.commit()
                    await self.db.refresh(room)

                    processed_count += 1
                    processed_ids.append(check_in.id)

                    # Broadcast WebSocket event for real-time UI update
                    await websocket_manager.broadcast({
                        "event": "overtime_auto_cutoff",
                        "data": {
                            "check_in_id": check_in.id,
                            "room_id": room.id,
                            "room_number": room.room_number,
                            "old_status": old_status.value,
                            "new_status": RoomStatus.OCCUPIED_OVERTIME.value,
                            "overtime_minutes": overtime_minutes,
                            "expected_checkout": check_in.expected_check_out_time.isoformat(),
                            "current_time": now.isoformat(),
                            "customer_name": check_in.customer.full_name if check_in.customer else "N/A",
                            "timestamp": now.isoformat()
                        }
                    })

                    print(f"✅ [OVERTIME] Room {room.room_number} → OCCUPIED_OVERTIME "
                          f"(Check-in #{check_in.id}, {overtime_minutes} mins over)")

                else:
                    # Room is not in OCCUPIED status (maybe already checked out?)
                    # Still mark check_in as overtime but don't change room status
                    await self.db.commit()
                    print(f"⚠️ [OVERTIME] Check-in #{check_in.id} marked as overtime, "
                          f"but room {check_in.room_id} status is {room.status.value if room else 'N/A'}")

            except Exception as e:
                await self.db.rollback()
                print(f"❌ Error processing overtime for check-in #{check_in.id}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        return {
            "success": True,
            "current_time": now.isoformat(),
            "total_checked": len(overtime_check_ins),
            "overtime_found": len(overtime_check_ins),
            "rooms_updated": processed_count,
            "processed_check_ins": processed_ids
        }

    async def get_current_overtime_stays(self) -> List[CheckIn]:
        """
        Get all current overtime stays (for reporting/monitoring)

        Returns:
            List of CheckIn objects that are currently in overtime status
        """
        stmt = select(CheckIn).options(
            selectinload(CheckIn.room),
            selectinload(CheckIn.customer)
        ).where(
            and_(
                CheckIn.stay_type == StayTypeEnum.TEMPORARY,
                CheckIn.status == CheckInStatusEnum.CHECKED_IN,
                CheckIn.is_overtime == 1
            )
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

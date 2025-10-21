"""
Booking API Endpoints (Phase 7)
Handles booking creation, updates, calendar view, and availability checks
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date

from app.core.dependencies import get_db, get_current_user, require_admin_or_reception
from app.models.user import User
from app.services.booking_service import BookingService
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse,
    BookingCalendarEvent,
    PublicHoliday,
    RoomAvailabilityCheck,
    RoomAvailabilityResponse
)

router = APIRouter()


# ==================== Booking CRUD ====================

@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(require_admin_or_reception),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new booking

    **Required role**: Admin, Reception

    **Request Body**:
    - customer_id: Customer ID
    - room_id: Room ID
    - check_in_date: Check-in date (YYYY-MM-DD)
    - check_out_date: Check-out date (YYYY-MM-DD)
    - total_amount: Total booking amount
    - deposit_amount: Deposit amount (optional, default 0)
    - notes: Booking notes (optional)

    **Returns**: Created booking with details
    """
    try:
        service = BookingService(db)
        booking = await service.create_booking(booking_data, current_user.id)

        # Prepare response
        return await _map_booking_to_response(booking)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error creating booking: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/", response_model=BookingListResponse)
async def get_bookings(
    status: Optional[str] = Query(None, description="Filter by status"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_admin_or_reception),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of bookings with filters

    **Required role**: Admin, Reception

    **Query Parameters**:
    - status: Filter by status (pending, confirmed, checked_in, completed, cancelled)
    - room_id: Filter by room ID
    - customer_id: Filter by customer ID
    - start_date: Filter by check-in date >= start_date
    - end_date: Filter by check-out date <= end_date
    - skip: Pagination offset
    - limit: Items per page

    **Returns**: List of bookings with pagination info
    """

    try:
        from app.models.booking import BookingStatusEnum

        # Convert status string to enum if provided
        status_enum = None
        if status:
            try:
                status_enum = BookingStatusEnum(status.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        service = BookingService(db)
        bookings, total = await service.get_bookings(
            status=status_enum,
            room_id=room_id,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )

        # Map to response
        booking_responses = []
        for booking in bookings:
            response = await _map_booking_to_response(booking)
            booking_responses.append(response)

        return BookingListResponse(
            data=booking_responses,
            total=total,
            skip=skip,
            limit=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting bookings: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(require_admin_or_reception),
    db: AsyncSession = Depends(get_db)
):
    """
    Get booking by ID

    **Required role**: Admin, Reception

    **Path Parameters**:
    - booking_id: Booking ID

    **Returns**: Booking details
    """

    try:
        service = BookingService(db)
        booking = await service.get_booking_by_id(booking_id, include_relations=True)

        if not booking:
            raise HTTPException(status_code=404, detail="ไม่พบการจองที่ระบุ")

        return await _map_booking_to_response(booking)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting booking: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    current_user: User = Depends(require_admin_or_reception),
    db: AsyncSession = Depends(get_db)
):
    """
    Update booking

    **Required role**: Admin, Reception

    **Path Parameters**:
    - booking_id: Booking ID

    **Request Body** (all optional):
    - check_in_date: New check-in date
    - check_out_date: New check-out date
    - total_amount: New total amount
    - deposit_amount: New deposit amount
    - notes: New notes

    **Returns**: Updated booking details
    """

    try:
        service = BookingService(db)
        booking = await service.update_booking(booking_id, booking_data, current_user.id)

        return await _map_booking_to_response(booking)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error updating booking: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.delete("/{booking_id}", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(require_admin_or_reception),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel booking

    **Required role**: Admin, Reception

    **Path Parameters**:
    - booking_id: Booking ID

    **Returns**: Cancelled booking details

    **Note**: Deposits are non-refundable
    """

    try:
        service = BookingService(db)
        booking = await service.cancel_booking(booking_id, current_user.id)

        return await _map_booking_to_response(booking)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error cancelling booking: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


# ==================== Calendar & Availability ====================

@router.get("/calendar/events", response_model=List[BookingCalendarEvent])
async def get_calendar_events(
    start_date: date = Query(..., description="Calendar start date"),
    end_date: date = Query(..., description="Calendar end date"),
    current_user: User = Depends(require_admin_or_reception),
    db: AsyncSession = Depends(get_db)
):
    """
    Get bookings as calendar events

    **Required role**: Admin, Reception

    **Query Parameters**:
    - start_date: Calendar view start date (YYYY-MM-DD)
    - end_date: Calendar view end date (YYYY-MM-DD)

    **Returns**: List of calendar events (bookings)
    """

    try:
        service = BookingService(db)
        events = await service.get_calendar_events(start_date, end_date)

        return events

    except Exception as e:
        print(f"Error getting calendar events: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/calendar/public-holidays/{year}", response_model=List[PublicHoliday])
async def get_public_holidays(
    year: int,
    current_user: User = Depends(require_admin_or_reception),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Thai public holidays for a specific year

    **Required role**: Admin, Reception

    **Path Parameters**:
    - year: Year (e.g., 2025)

    **Returns**: List of public holidays
    """

    try:
        service = BookingService(db)
        holidays = await service.get_public_holidays(year)

        return holidays

    except Exception as e:
        print(f"Error getting public holidays: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/check-availability", response_model=RoomAvailabilityResponse)
async def check_room_availability(
    availability_check: RoomAvailabilityCheck,
    current_user: User = Depends(require_admin_or_reception),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if a room is available for given dates

    **Required role**: Admin, Reception

    **Request Body**:
    - room_id: Room ID to check
    - check_in_date: Check-in date
    - check_out_date: Check-out date
    - exclude_booking_id: Booking ID to exclude (for editing)

    **Returns**: Availability status and conflicting bookings if any
    """

    try:
        service = BookingService(db)

        # Check availability
        is_available = await service.check_room_availability(
            room_id=availability_check.room_id,
            check_in_date=availability_check.check_in_date,
            check_out_date=availability_check.check_out_date,
            exclude_booking_id=availability_check.exclude_booking_id
        )

        # If not available, get conflicting bookings
        conflicting = []
        if not is_available:
            conflicting_bookings = await service.get_conflicting_bookings(
                room_id=availability_check.room_id,
                check_in_date=availability_check.check_in_date,
                check_out_date=availability_check.check_out_date,
                exclude_booking_id=availability_check.exclude_booking_id
            )

            for booking in conflicting_bookings:
                response = await _map_booking_to_response(booking)
                conflicting.append(response)

        return RoomAvailabilityResponse(
            available=is_available,
            conflicting_bookings=conflicting
        )

    except Exception as e:
        print(f"Error checking availability: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


# ==================== Helper Functions ====================

async def _map_booking_to_response(booking) -> BookingResponse:
    """Map Booking model to BookingResponse schema"""
    return BookingResponse(
        id=booking.id,
        customer_id=booking.customer_id,
        room_id=booking.room_id,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        number_of_nights=booking.number_of_nights,
        total_amount=booking.total_amount,
        deposit_amount=booking.deposit_amount,
        status=booking.status.value,
        notes=booking.notes,
        created_by=booking.created_by,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
        cancelled_at=booking.cancelled_at,
        # Related data
        customer_name=booking.customer.full_name if booking.customer else None,
        customer_phone=booking.customer.phone_number if booking.customer else None,
        room_number=booking.room.room_number if booking.room else None,
        room_type_name=booking.room.room_type.name if booking.room and booking.room.room_type else None,
        creator_name=booking.creator.full_name if booking.creator else None
    )
"""
Check-In API Endpoints (Phase 4)
Handles check-in operations for rooms
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.models import User
from app.services import CheckInService, CheckOutService, CustomerService
from app.schemas.check_in import (
    CheckInCreate,
    CheckInCreateWithCustomer,
    CheckInResponse,
    CheckInWithDetails,
    CheckOutRequest,
    CheckOutSummary
)
from app.schemas.customer import CustomerCreate

router = APIRouter()


@router.post("/", response_model=CheckInResponse)
async def create_check_in(
    request_data: CheckInCreateWithCustomer,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new check-in

    Requires authentication and Reception or Admin role.

    Request Body:
        - check_in_data: Check-in information (room_id, stay_type, etc.)
        - customer_data: Customer information (name, phone, etc.)

    Returns:
        Created check-in record

    Business Logic:
        - Validates room is available
        - Creates or updates customer record by phone number
        - Calculates expected checkout time based on stay type
        - Updates room status to 'occupied'
        - Broadcasts WebSocket event
    """
    try:
        # Parse customer data from request
        customer_data = CustomerCreate(**request_data.customer_data)

        # Get or create customer
        customer_service = CustomerService(db)
        customer, _ = await customer_service.get_or_create_customer(customer_data)

        # Create check-in data object (without customer_data field)
        check_in_data = CheckInCreate(
            room_id=request_data.room_id,
            stay_type=request_data.stay_type,
            number_of_nights=request_data.number_of_nights,
            number_of_guests=request_data.number_of_guests,
            check_in_time=request_data.check_in_time,
            booking_id=request_data.booking_id,
            deposit_amount=request_data.deposit_amount,
            payment_method=request_data.payment_method,
            notes=request_data.notes
        )

        # Create check-in
        check_in_service = CheckInService(db)
        check_in = await check_in_service.create_check_in(
            check_in_data=check_in_data,
            customer_id=customer.id,
            created_by_user_id=current_user.id
        )

        return CheckInResponse.model_validate(check_in)

    except ValueError as e:
        # Log the error for debugging
        print(f"ValueError in check-in: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the error for debugging
        print(f"Exception in check-in: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/{check_in_id}", response_model=CheckInResponse)
async def get_check_in(
    check_in_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get check-in details by ID

    Requires authentication.

    Returns:
        Check-in record with relationships loaded
    """
    service = CheckInService(db)
    check_in = await service.get_check_in_by_id(check_in_id)

    if not check_in:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการเช็คอิน")

    return CheckInResponse.model_validate(check_in)


@router.get("/room/{room_id}/active", response_model=CheckInResponse)
async def get_active_check_in_by_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get active check-in for a specific room

    Requires authentication.

    Returns:
        Active check-in record or 404 if no active check-in
    """
    service = CheckInService(db)
    check_in = await service.get_active_check_in_by_room(room_id)

    if not check_in:
        raise HTTPException(status_code=404, detail="ไม่พบการเช็คอินที่กำลังดำเนินการ")

    return CheckInResponse.model_validate(check_in)


@router.get("/{check_in_id}/checkout-summary", response_model=CheckOutSummary)
async def get_checkout_summary(
    check_in_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get checkout summary with calculated amounts

    Requires authentication and Reception or Admin role.

    Returns:
        Checkout summary including:
        - Base amount
        - Overtime status and charges
        - Total amount (before extra charges/discounts)
    """
    try:
        service = CheckOutService(db)
        summary = await service.get_checkout_summary(check_in_id)
        return summary

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/{check_in_id}/checkout", response_model=CheckInResponse)
async def process_checkout(
    check_in_id: int,
    checkout_data: CheckOutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process check-out for a check-in

    Requires authentication and Reception or Admin role.

    Request Body:
        - actual_check_out_time: Optional override for checkout time
        - extra_charges: Additional charges (e.g., minibar, damage)
        - discount_amount: Discount amount
        - discount_reason: Reason for discount
        - payment_method: Payment method used

    Returns:
        Updated check-in record

    Business Logic:
        - Calculates overtime charges if applicable
        - Applies extra charges and discounts
        - Records payment
        - Updates room status to 'cleaning'
        - Creates housekeeping notification
        - Broadcasts WebSocket events
    """
    try:
        service = CheckOutService(db)
        check_in = await service.process_check_out(
            check_in_id=check_in_id,
            checkout_data=checkout_data,
            processed_by_user_id=current_user.id
        )

        return CheckInResponse.model_validate(check_in)

    except ValueError as e:
        print(f"ValueError in checkout: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception in checkout: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

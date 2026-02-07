"""
Check-In API Endpoints (Phase 4)
Handles check-in operations for rooms
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import os
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.models import User, CheckIn, Customer, Room, RoomType
from app.services import CheckInService, CheckOutService, CustomerService, PDFService, SettingsService
from app.schemas.check_in import (
    CheckInCreate,
    CheckInCreateWithCustomer,
    CheckInResponse,
    CheckInWithDetails,
    CheckOutRequest,
    CheckOutSummary,
    RoomTransferRequest,
    RoomTransferResponse
)
from app.schemas.customer import CustomerCreate

import logging

logger = logging.getLogger(__name__)

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
        logger.warning("ValueError in check-in: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Exception in check-in: %s", str(e))
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
        logger.warning("ValueError in checkout: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Exception in checkout: %s", str(e))
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/{check_in_id}/generate-receipt")
async def generate_receipt(
    check_in_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PDF receipt for a checked-out check-in

    Requires authentication.

    Returns:
        PDF file as streaming response

    Business Logic:
        - Validates check-in exists and is checked out
        - Generates PDF receipt with:
          - Hotel information
          - Customer details
          - Room details
          - Charges breakdown (base, overtime, extra, discount)
          - Payment method
          - Receipt number and date
    """
    try:
        # Get check-in with all related data
        result = await db.execute(
            select(CheckIn)
            .options(
                selectinload(CheckIn.customer),
                selectinload(CheckIn.room).selectinload(Room.room_type),
                selectinload(CheckIn.checkout_user)
            )
            .where(CheckIn.id == check_in_id)
        )
        check_in = result.scalar_one_or_none()

        if not check_in:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการเช็คอิน")

        if check_in.status != "checked_out":
            raise HTTPException(status_code=400, detail="ยังไม่ได้เช็คเอาท์")

        # Build checkout summary from stored check-in data (already checked out)
        from app.schemas.check_in import CheckOutSummary
        checkout_summary = CheckOutSummary(
            check_in_id=check_in.id,
            room_number=check_in.room.room_number,
            customer_name=check_in.customer.full_name,
            stay_type=check_in.stay_type,
            check_in_time=check_in.check_in_time,
            expected_check_out_time=check_in.expected_check_out_time,
            actual_check_out_time=check_in.actual_check_out_time or check_in.check_in_time,
            base_amount=check_in.base_amount,
            is_overtime=bool(check_in.is_overtime),
            overtime_minutes=check_in.overtime_minutes,
            overtime_charge=check_in.overtime_charge,
            extra_charges=check_in.extra_charges,
            discount_amount=check_in.discount_amount,
            total_amount=check_in.total_amount
        )

        # Fetch hotel info from settings
        settings_service = SettingsService(db)
        general_settings = await settings_service.get_general_settings()

        # Generate PDF
        pdf_service = PDFService()
        pdf_buffer = pdf_service.generate_receipt(
            check_in=check_in,
            customer=check_in.customer,
            room=check_in.room,
            room_type=check_in.room.room_type,
            checkout_summary=checkout_summary,
            checked_out_by=check_in.checkout_user,
            hotel_name=general_settings.hotel_name or "Flying Hotel",
            hotel_address=general_settings.hotel_address or "123 ถนนสุขุมวิท กรุงเทพฯ 10110",
            hotel_phone=general_settings.hotel_phone or "02-123-4567"
        )

        # Create filename
        receipt_no = f"R{check_in.id:06d}"
        filename = f"receipt_{receipt_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating receipt: %s", str(e))
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการสร้างใบเสร็จ: {str(e)}")


@router.post("/{check_in_id}/upload-slip")
async def upload_payment_slip(
    check_in_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload payment slip image for a check-in

    Requires authentication and Reception or Admin role.

    Args:
        check_in_id: Check-in ID
        file: Image file (JPG, PNG)

    Returns:
        Success message with file URL

    Business Logic:
        - Validates file type (image only)
        - Saves file to uploads directory
        - Updates check-in record with payment_slip_url
    """
    try:
        # Validate check-in exists
        result = await db.execute(
            select(CheckIn).where(CheckIn.id == check_in_id)
        )
        check_in = result.scalar_one_or_none()

        if not check_in:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการเช็คอิน")

        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="รองรับเฉพาะไฟล์รูปภาพ (JPG, PNG)"
            )

        # Create uploads directory if not exists
        upload_dir = "/app/uploads/payment_slips"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate filename
        file_ext = file.filename.split(".")[-1]
        filename = f"slip_{check_in_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
        file_path = os.path.join(upload_dir, filename)

        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Update check-in record
        check_in.payment_slip_url = f"/uploads/payment_slips/{filename}"
        await db.commit()

        return {
            "message": "อัปโหลดสลิปสำเร็จ",
            "file_url": check_in.payment_slip_url
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error uploading slip: %s", str(e))
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการอัปโหลดสลิป: {str(e)}")


@router.post("/{check_in_id}/transfer-room", response_model=RoomTransferResponse)
async def transfer_room(
    check_in_id: int,
    transfer_data: RoomTransferRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transfer guest from current room to a new room

    Requires authentication and Reception or Admin role.

    Request Body:
        - new_room_id: ID of the new room to transfer to
        - reason: Optional reason for transfer

    Returns:
        Transfer details including old and new room information

    Business Logic:
        - Validates check-in is active
        - Validates new room is available
        - Validates new room is same room type (VIP → VIP only)
        - Updates check_in.room_id to new room
        - Updates old room status to 'cleaning'
        - Updates new room status to 'occupied'
        - TODO Phase 5: Creates housekeeping task for old room
        - TODO Phase 5: Sends Telegram notification
        - Broadcasts WebSocket events

    Validation Rules:
        - Can only transfer active check-ins (status = 'checked_in')
        - New room must be 'available' or 'reserved'
        - New room must be same room type as old room
        - Cannot transfer to the same room
    """
    try:
        service = CheckInService(db)
        check_in, old_room, new_room = await service.transfer_room(
            check_in_id=check_in_id,
            new_room_id=transfer_data.new_room_id,
            reason=transfer_data.reason,
            transferred_by_user_id=current_user.id
        )

        from app.core.datetime_utils import now_thailand

        return RoomTransferResponse(
            check_in_id=check_in.id,
            old_room_id=old_room.id,
            old_room_number=old_room.room_number,
            new_room_id=new_room.id,
            new_room_number=new_room.room_number,
            transferred_by=current_user.id,
            transferred_at=now_thailand(),
            reason=transfer_data.reason,
            message=f"ย้ายห้องจาก {old_room.room_number} ไป {new_room.room_number} สำเร็จ"
        )

    except ValueError as e:
        logger.warning("ValueError in room transfer: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Exception in room transfer: %s", str(e))
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

"""
Public API Endpoints (Phase 5.1 & 6)
Public endpoints that don't require authentication
Used for:
- Telegram bot links for staff
- Guest QR code ordering system
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from io import BytesIO
import qrcode

from app.core.dependencies import get_db
from app.services.housekeeping_service import HousekeepingService
from app.services.maintenance_service import MaintenanceService
from app.models import Room, Product, Order, CheckIn
from app.models.check_in import CheckInStatusEnum
from app.schemas.housekeeping import (
    HousekeepingTaskWithDetails,
    HousekeepingTaskStartRequest,
    HousekeepingTaskCompleteRequest
)
from app.schemas.maintenance import (
    MaintenanceTaskResponse,
    MaintenanceTaskStartRequest,
    MaintenanceTaskCompleteRequest,
    MaintenanceTaskCreate
)

router = APIRouter()


# ==================== Housekeeping Public Endpoints ====================

@router.get("/housekeeping/tasks/{task_id}", response_model=HousekeepingTaskWithDetails)
async def get_public_housekeeping_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get housekeeping task details (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow housekeeping staff
    to view task details without logging in.

    Path Parameters:
        - task_id: Task ID

    Returns:
        Housekeeping task with full details
    """
    try:
        service = HousekeepingService(db)
        task = await service.get_task_by_id(task_id, include_relations=True)

        if not task:
            raise HTTPException(status_code=404, detail="ไม่พบงานทำความสะอาด")

        task_dict = {
            "id": task.id,
            "room_id": task.room_id,
            "check_in_id": task.check_in_id,
            "assigned_to": task.assigned_to,
            "status": task.status,
            "priority": task.priority,
            "title": task.title,
            "description": task.description,
            "notes": task.notes,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "duration_minutes": task.duration_minutes,
            "created_by": task.created_by,
            "completed_by": task.completed_by,
            "updated_at": task.updated_at,
            "room_number": task.room.room_number if task.room else None,
            "room_type_name": task.room.room_type.name if task.room and task.room.room_type else None,
            "assigned_user_name": task.assigned_user.full_name if task.assigned_user else None,
            "creator_name": task.creator.full_name if task.creator else None,
            "completer_name": task.completer.full_name if task.completer else None
        }

        return HousekeepingTaskWithDetails(**task_dict)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting public housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/housekeeping/tasks/{task_id}/start")
async def start_public_housekeeping_task(
    task_id: int,
    start_data: HousekeepingTaskStartRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Start housekeeping task (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow housekeeping staff
    to start tasks without logging in.

    Path Parameters:
        - task_id: Task ID

    Request Body:
        - started_at: Optional start time (defaults to now)

    Note: Since there's no authentication, the task will be started without
    assigning to a specific user (unless already assigned).
    """
    try:
        service = HousekeepingService(db)

        # Get task to check if it's already assigned
        task = await service.get_task_by_id(task_id, include_relations=False)
        if not task:
            raise HTTPException(status_code=404, detail="ไม่พบงานทำความสะอาด")

        # Use assigned user if exists, otherwise use a default user_id
        # In production, you might want to create a special "telegram_bot" user
        user_id = task.assigned_to if task.assigned_to else 1  # Default to admin user

        task = await service.start_task(
            task_id=task_id,
            user_id=user_id,
            started_at=start_data.started_at
        )

        return {
            "success": True,
            "message": "เริ่มงานทำความสะอาดเรียบร้อย",
            "task_id": task.id,
            "status": task.status
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting public housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/housekeeping/tasks/{task_id}/complete")
async def complete_public_housekeeping_task(
    task_id: int,
    complete_data: HousekeepingTaskCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete housekeeping task (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow housekeeping staff
    to complete tasks without logging in.

    Path Parameters:
        - task_id: Task ID

    Request Body:
        - completed_at: Optional completion time (defaults to now)
        - notes: Completion notes (optional)
    """
    try:
        service = HousekeepingService(db)

        # Get task to check if it's already assigned
        task = await service.get_task_by_id(task_id, include_relations=False)
        if not task:
            raise HTTPException(status_code=404, detail="ไม่พบงานทำความสะอาด")

        # Use assigned user if exists, otherwise use a default user_id
        user_id = task.assigned_to if task.assigned_to else 1  # Default to admin user

        task = await service.complete_task(
            task_id=task_id,
            user_id=user_id,
            completed_at=complete_data.completed_at,
            notes=complete_data.notes
        )

        return {
            "success": True,
            "message": "ทำความสะอาดเสร็จสิ้นเรียบร้อย",
            "task_id": task.id,
            "status": task.status,
            "duration_minutes": task.duration_minutes
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing public housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


# ==================== Maintenance Public Endpoints ====================

@router.get("/maintenance/tasks/{task_id}", response_model=MaintenanceTaskResponse)
async def get_public_maintenance_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get maintenance task details (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow maintenance staff
    to view task details without logging in.

    Path Parameters:
        - task_id: Task ID

    Returns:
        Maintenance task with full details
    """
    try:
        service = MaintenanceService(db)
        task = await service.get_task_by_id(task_id)

        return MaintenanceTaskResponse.model_validate(task)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error getting public maintenance task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/maintenance/tasks/{task_id}/start")
async def start_public_maintenance_task(
    task_id: int,
    start_data: MaintenanceTaskStartRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Start maintenance task (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow maintenance staff
    to start tasks without logging in.

    Path Parameters:
        - task_id: Task ID

    Request Body:
        - started_at: Optional start time (defaults to now)
    """
    try:
        service = MaintenanceService(db)

        # Get task to check if it's already assigned
        task = await service.get_task_by_id(task_id)

        # Use assigned user if exists, otherwise use a default user_id
        user_id = task.assigned_to if task.assigned_to else 1  # Default to admin user

        task = await service.start_task(
            task_id=task_id,
            user_id=user_id,
            started_at=start_data.started_at
        )

        return {
            "success": True,
            "message": "เริ่มงานซ่อมบำรุงเรียบร้อย",
            "task_id": task.id,
            "status": task.status
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error starting public maintenance task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/maintenance/tasks/{task_id}/complete")
async def complete_public_maintenance_task(
    task_id: int,
    complete_data: MaintenanceTaskCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete maintenance task (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow maintenance staff
    to complete tasks without logging in.

    Path Parameters:
        - task_id: Task ID

    Request Body:
        - completed_at: Optional completion time (defaults to now)
        - notes: Completion notes (optional)
    """
    try:
        service = MaintenanceService(db)

        # Get task to check if it's already assigned
        task = await service.get_task_by_id(task_id)

        # Use assigned user if exists, otherwise use a default user_id
        user_id = task.assigned_to if task.assigned_to else 1  # Default to admin user

        task = await service.complete_task(
            task_id=task_id,
            user_id=user_id,
            completed_at=complete_data.completed_at,
            notes=complete_data.notes
        )

        return {
            "success": True,
            "message": "งานซ่อมบำรุงเสร็จสิ้นเรียบร้อย",
            "task_id": task.id,
            "status": task.status,
            "duration_minutes": task.duration_minutes
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error completing public maintenance task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/maintenance/report")
async def report_public_maintenance(
    report_data: MaintenanceTaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create maintenance task report (PUBLIC - no authentication required)

    This endpoint is used by housekeeping staff (via public links) to report
    damage or maintenance needs they discover while cleaning.

    Request Body:
        - room_id: Room ID
        - title: Task title
        - description: Task description (optional)
        - category: Task category (plumbing, electrical, hvac, furniture, appliance, building, other)
        - priority: Priority level (urgent, high, medium, low)
        - assigned_to: Assigned user ID (optional)

    Returns:
        Created maintenance task
    """
    try:
        service = MaintenanceService(db)

        # Create task using default user (admin) as creator since no auth
        # In production, you might want to create a special "housekeeping_report" user
        creator_user_id = 1  # Default to admin user

        task = await service.create_task(report_data, creator_user_id)

        return {
            "success": True,
            "message": "แจ้งซ่อมบำรุงเรียบร้อย",
            "task_id": task.id,
            "room_id": task.room_id
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error creating public maintenance report: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


# ==================== Guest QR Code Ordering (Phase 6) ====================

@router.get("/qrcode/room/{room_id}")
async def get_room_qrcode(
    room_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate QR code for room ordering page

    Returns PNG image of QR code that links to guest order page
    """
    try:
        # Verify room exists
        room = await db.get(Room, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="ไม่พบห้องนี้")

        # Create QR code with guest order page URL
        # URL format: Full URL for QR code to work across devices
        qr_url = f"http://localhost:5173/public/guest/room/{room_id}/order"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        return StreamingResponse(img_bytes, media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/qrcode/all-rooms")
async def get_all_room_qrcodes(
    db: AsyncSession = Depends(get_db)
):
    """
    Get QR code data for all active rooms (for admin)

    Returns list of rooms with their QR code URLs
    """
    try:
        stmt = (
            select(Room)
            .where(Room.is_active == True)
            .order_by(Room.floor, Room.room_number)
        )

        result = await db.execute(stmt)
        rooms = result.scalars().all()

        qr_codes = []
        for room in rooms:
            # URL format: Full URL for QR code to work across devices
            # Note: In production, this should use the actual domain from request
            qr_url = f"http://localhost:5173/public/guest/room/{room.id}/order"

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64 for JSON response
            import base64
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

            qr_codes.append({
                "room_id": room.id,
                "room_number": room.room_number,
                "floor": room.floor,
                "qr_code_base64": f"data:image/png;base64,{img_base64}",
                "qr_url": qr_url,
                "download_url": f"/api/v1/public/qrcode/room/{room.id}"
            })

        return qr_codes

    except Exception as e:
        print(f"Error generating QR codes: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/guest/room/{room_id}/check-in-status")
async def get_guest_checkin_status(
    room_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if room has active check-in

    Used by guest order page to verify guest can order
    """
    try:
        # Check for active check-in in this room
        stmt = (
            select(CheckIn)
            .where(
                CheckIn.room_id == room_id,
                CheckIn.status == CheckInStatusEnum.CHECKED_IN
            )
        )

        result = await db.execute(stmt)
        check_in = result.scalar_one_or_none()

        if not check_in:
            raise HTTPException(status_code=404, detail="ห้องนี้ไม่มีการเข้าพัก")

        return {
            "room_id": room_id,
            "check_in_id": check_in.id,
            "customer_name": check_in.customer.full_name if check_in.customer else "ลูกค้า",
            "active": True
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error checking check-in status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/guest/products")
async def get_guest_products(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all available products for guest ordering
    """
    try:
        stmt = (
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.name)
        )

        result = await db.execute(stmt)
        products = result.scalars().all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "price": float(p.price),
                "is_active": p.is_active
            }
            for p in products
        ]

    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/guest/room/{room_id}/order")
async def create_guest_order(
    room_id: int,
    order_items: dict,  # {"items": [{"product_id": 1, "quantity": 2}]}
    db: AsyncSession = Depends(get_db)
):
    """
    Create order from guest QR code

    order_items format:
    {
      "items": [
        {"product_id": 1, "quantity": 2},
        {"product_id": 3, "quantity": 1}
      ]
    }
    """
    try:
        # Verify room has active check-in
        stmt = (
            select(CheckIn)
            .where(
                CheckIn.room_id == room_id,
                CheckIn.status == CheckInStatusEnum.CHECKED_IN
            )
        )

        result = await db.execute(stmt)
        check_in = result.scalar_one_or_none()

        if not check_in:
            raise HTTPException(status_code=403, detail="ห้องนี้ไม่มีการเข้าพัก")

        # Validate and create order items
        total_amount = 0
        order_details = []

        for item in order_items.get("items", []):
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            if not product_id or quantity <= 0:
                raise HTTPException(status_code=400, detail="ข้อมูลสินค้าไม่ถูกต้อง")

            product = await db.get(Product, product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"ไม่พบสินค้า ID {product_id}")

            item_total = float(product.price) * quantity
            total_amount += item_total

            order_details.append({
                "product_id": product_id,
                "product_name": product.name,
                "quantity": quantity,
                "unit_price": float(product.price),
                "total": item_total
            })

        # Create order
        from app.core.datetime_utils import now_thailand
        order = Order(
            check_in_id=check_in.id,
            room_id=room_id,
            order_date=now_thailand(),
            status="pending",
            total_amount=total_amount,
            notes=f"Guest QR order - {len(order_details)} items"
        )

        db.add(order)
        await db.flush()
        await db.commit()
        await db.refresh(order)

        return {
            "success": True,
            "message": "สั่งของเรียบร้อย",
            "order_id": order.id,
            "room_id": room_id,
            "total_amount": total_amount,
            "items": order_details
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating guest order: {str(e)}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

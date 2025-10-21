"""
Order Management Endpoints (Phase 6)
Reception endpoints for managing guest orders
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime, timedelta

from app.core.dependencies import get_db, get_current_user, require_role
from app.models import Order, CheckIn, Room, Product, User
from app.models.check_in import CheckInStatusEnum
from app.schemas.order import OrderResponse, OrderListResponse

router = APIRouter()


@router.get("", response_model=OrderListResponse)
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    room_id: int = Query(None),
    check_in_id: int = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["RECEPTION", "ADMIN"]))
):
    """
    Get orders for reception management

    Query Parameters:
        - skip: Number of items to skip
        - limit: Number of items to return (1-100)
        - status: Filter by status (pending, delivered, completed)
        - room_id: Filter by room ID
        - check_in_id: Filter by check-in ID
        - date_from: Filter orders from date (YYYY-MM-DD)
        - date_to: Filter orders to date (YYYY-MM-DD)

    Returns:
        List of orders with pagination info
    """
    try:
        stmt = select(Order)

        # Add filters
        filters = []

        if status:
            filters.append(Order.status == status)

        if room_id:
            # Join with CheckIn to filter by room
            stmt = stmt.join(CheckIn).where(CheckIn.room_id == room_id)

        if check_in_id:
            filters.append(Order.check_in_id == check_in_id)

        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                filters.append(Order.ordered_at >= from_date)
            except ValueError:
                pass

        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
                filters.append(Order.ordered_at < to_date)
            except ValueError:
                pass

        if filters:
            stmt = stmt.where(and_(*filters))

        # Get total count
        count_stmt = select(Order)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())

        # Apply pagination and ordering
        stmt = stmt.order_by(Order.ordered_at.desc()).offset(skip).limit(limit)

        result = await db.execute(stmt)
        orders = result.scalars().all()

        return OrderListResponse(
            orders=[OrderResponse.from_orm(o) for o in orders],
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        print(f"Error fetching orders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["RECEPTION", "ADMIN"]))
):
    """
    Get order details by ID

    Path Parameters:
        - order_id: Order ID

    Returns:
        Order details with product information
    """
    try:
        order = await db.get(Order, order_id)

        if not order:
            raise HTTPException(status_code=404, detail="ไม่พบคำสั่ง")

        return OrderResponse.from_orm(order)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["RECEPTION", "ADMIN"]))
):
    """
    Update order status (pending -> delivered -> completed)

    Path Parameters:
        - order_id: Order ID

    Request Body:
        - new_status: New status (pending, delivered, completed)

    Returns:
        Updated order
    """
    try:
        # Validate status
        valid_statuses = ["pending", "delivered", "completed"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"สถานะไม่ถูกต้อง ต้องเป็น {', '.join(valid_statuses)}"
            )

        order = await db.get(Order, order_id)

        if not order:
            raise HTTPException(status_code=404, detail="ไม่พบคำสั่ง")

        # Update status
        order.status = new_status

        if new_status == "delivered":
            from app.core.datetime_utils import now_thailand
            order.delivered_at = now_thailand()

        await db.commit()
        await db.refresh(order)

        return OrderResponse.from_orm(order)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error updating order status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/{order_id}/complete")
async def complete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["RECEPTION", "ADMIN"]))
):
    """
    Mark order as completed (for paid/delivered items)

    Path Parameters:
        - order_id: Order ID

    Returns:
        Updated order
    """
    try:
        order = await db.get(Order, order_id)

        if not order:
            raise HTTPException(status_code=404, detail="ไม่พบคำสั่ง")

        order.status = "completed"

        await db.commit()
        await db.refresh(order)

        return OrderResponse.from_orm(order)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error completing order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

"""
Order Schemas (Phase 6)
Request/Response schemas for order management
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.order import OrderSourceEnum, OrderStatusEnum


class OrderResponse(BaseModel):
    """Schema for order responses"""
    id: int
    check_in_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    order_source: OrderSourceEnum
    status: OrderStatusEnum
    ordered_at: datetime
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True


class OrderListResponse(BaseModel):
    """Schema for order list responses"""
    orders: List[OrderResponse]
    total: int
    skip: int
    limit: int

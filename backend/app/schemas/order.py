"""
Order Schemas (Phase 6)
Request/Response schemas for order management
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OrderResponse(BaseModel):
    """Schema for order responses"""
    id: int
    check_in_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    order_source: str
    status: str
    ordered_at: datetime
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Convert ORM model to schema"""
        return cls(
            id=obj.id,
            check_in_id=obj.check_in_id,
            product_id=obj.product_id,
            quantity=obj.quantity,
            unit_price=float(obj.unit_price),
            total_price=float(obj.total_price),
            order_source=obj.order_source.value if hasattr(obj.order_source, 'value') else obj.order_source,
            status=obj.status.value if hasattr(obj.status, 'value') else obj.status,
            ordered_at=obj.ordered_at,
            delivered_at=obj.delivered_at,
            created_at=obj.created_at
        )


class OrderListResponse(BaseModel):
    """Schema for order list responses"""
    orders: List[OrderResponse]
    total: int
    skip: int
    limit: int

"""
Order Model (Phase 3 - Basic, Full implementation in Phase 6)
Guest orders for additional items
"""
from sqlalchemy import Column, Integer, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class OrderSourceEnum(str, enum.Enum):
    """Order source enumeration"""
    QR_CODE = "QR_CODE"
    RECEPTION = "RECEPTION"


class OrderStatusEnum(str, enum.Enum):
    """Order status enumeration"""
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"


class Order(Base):
    """
    Order Model
    Stores guest orders (via QR code or reception)
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    # Relationships
    check_in_id = Column(Integer, ForeignKey("check_ins.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)

    # Order details
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    # Metadata
    order_source = Column(Enum(OrderSourceEnum), nullable=False)
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.PENDING, index=True)

    # Timestamps
    ordered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    check_in = relationship("CheckIn", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, check_in_id={self.check_in_id}, status={self.status})>"

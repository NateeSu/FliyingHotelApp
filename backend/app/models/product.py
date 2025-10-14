"""
Product Model (Phase 3 - Basic, Full implementation in Phase 6)
Products for guest orders (room amenities + food/beverage)
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Enum, Boolean, DateTime
from datetime import datetime
import enum

from app.db.base import Base


class ProductCategoryEnum(str, enum.Enum):
    """Product category enumeration"""
    ROOM_AMENITY = "room_amenity"
    FOOD_BEVERAGE = "food_beverage"


class Product(Base):
    """
    Product Model
    Stores products that guests can order
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    # Product information
    name = Column(String(255), nullable=False, index=True)
    category = Column(Enum(ProductCategoryEnum), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    is_chargeable = Column(Boolean, nullable=False, default=True)  # Some items might be complimentary
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"

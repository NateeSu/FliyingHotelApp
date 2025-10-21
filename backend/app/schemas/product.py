"""
Product Schemas (Phase 6)
Request/Response schemas for product management
"""
from pydantic import BaseModel, Field
from typing import Optional


class ProductCreate(BaseModel):
    """Schema for creating a new product"""
    name: str
    category: str
    price: float
    is_chargeable: bool = True
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None)
    price: Optional[float] = Field(None, ge=0)
    is_chargeable: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Schema for product responses"""
    id: int
    name: str
    category: str
    price: float
    is_chargeable: bool
    is_active: bool
    description: Optional[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Convert ORM model to schema"""
        return cls(
            id=obj.id,
            name=obj.name,
            category=obj.category.value if hasattr(obj.category, 'value') else obj.category,
            price=float(obj.price),
            is_chargeable=obj.is_chargeable,
            is_active=obj.is_active,
            description=obj.description
        )

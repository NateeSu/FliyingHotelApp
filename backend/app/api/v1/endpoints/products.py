"""
Product Management Endpoints (Phase 6)
Admin endpoints for managing products that guests can order
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from decimal import Decimal
from pydantic import BaseModel

from app.core.dependencies import get_db, get_current_user, require_role
from app.models import Product, User
from app.models.product import ProductCategoryEnum
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()


class ProductListResponse(BaseModel):
    """Response model for product list"""
    data: List[ProductResponse]
    total: int
    skip: int
    limit: int


@router.get("", response_model=ProductListResponse)
async def get_all_products(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all products (public - for guest order page)

    Query Parameters:
        - skip: Number of items to skip
        - limit: Number of items to return
        - category: Filter by category (room_amenity, food_beverage)

    Returns:
        List of active products with total count
    """
    try:
        # Get total count
        count_stmt = select(func.count(Product.id)).where(Product.is_active == True)
        if category:
            count_stmt = count_stmt.where(Product.category == category)

        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated products
        stmt = select(Product).where(Product.is_active == True)

        if category:
            stmt = stmt.where(Product.category == category)

        stmt = stmt.order_by(Product.name).offset(skip).limit(limit)

        result = await db.execute(stmt)
        products = result.scalars().all()

        return ProductListResponse(
            data=[ProductResponse.from_orm(p) for p in products],
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/admin/all", response_model=ProductListResponse)
async def get_all_products_admin(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RECEPTION"]))
):
    """
    Get all products including inactive (admin only)

    Query Parameters:
        - skip: Number of items to skip
        - limit: Number of items to return
        - include_inactive: Include inactive products

    Returns:
        List of all products with total count
    """

    try:
        # Get total count
        count_stmt = select(func.count(Product.id))
        if not include_inactive:
            count_stmt = count_stmt.where(Product.is_active == True)

        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated products
        stmt = select(Product)

        if not include_inactive:
            stmt = stmt.where(Product.is_active == True)

        stmt = stmt.order_by(Product.name).offset(skip).limit(limit)

        result = await db.execute(stmt)
        products = result.scalars().all()

        return ProductListResponse(
            data=[ProductResponse.from_orm(p) for p in products],
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get product details by ID

    Path Parameters:
        - product_id: Product ID

    Returns:
        Product details
    """
    try:
        product = await db.get(Product, product_id)

        if not product:
            raise HTTPException(status_code=404, detail="ไม่พบสินค้า")

        if not product.is_active:
            raise HTTPException(status_code=404, detail="ไม่พบสินค้า")

        return ProductResponse.from_orm(product)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """
    Create new product (admin only)

    Request Body:
        - name: Product name (required)
        - category: Product category (required)
        - price: Product price (required)
        - is_chargeable: Whether to charge for this item (default: true)
        - description: Product description (optional)

    Returns:
        Created product
    """

    try:
        # Check if product with same name already exists
        stmt = select(Product).where(Product.name == product_data.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="ชื่อสินค้านี้มีอยู่แล้ว")

        new_product = Product(
            name=product_data.name,
            category=product_data.category,
            price=product_data.price,
            is_chargeable=product_data.is_chargeable,
            description=product_data.description,
            is_active=True
        )

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

        return ProductResponse.from_orm(new_product)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """
    Update product (admin only)

    Path Parameters:
        - product_id: Product ID

    Request Body:
        - name: Product name (optional)
        - category: Product category (optional)
        - price: Product price (optional)
        - is_chargeable: Whether to charge for this item (optional)
        - description: Product description (optional)
        - is_active: Product status (optional)

    Returns:
        Updated product
    """

    try:
        product = await db.get(Product, product_id)

        if not product:
            raise HTTPException(status_code=404, detail="ไม่พบสินค้า")

        # Update fields if provided
        if product_data.name is not None:
            # Check if new name already exists
            stmt = select(Product).where(
                Product.name == product_data.name,
                Product.id != product_id
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                raise HTTPException(status_code=400, detail="ชื่อสินค้านี้มีอยู่แล้ว")

            product.name = product_data.name

        if product_data.category is not None:
            product.category = product_data.category

        if product_data.price is not None:
            product.price = product_data.price

        if product_data.is_chargeable is not None:
            product.is_chargeable = product_data.is_chargeable

        if product_data.description is not None:
            product.description = product_data.description

        if product_data.is_active is not None:
            product.is_active = product_data.is_active

        await db.commit()
        await db.refresh(product)

        return ProductResponse.from_orm(product)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error updating product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """
    Delete product (soft delete - set is_active to false) (admin only)

    Path Parameters:
        - product_id: Product ID

    Returns:
        Success message
    """

    try:
        product = await db.get(Product, product_id)

        if not product:
            raise HTTPException(status_code=404, detail="ไม่พบสินค้า")

        # Soft delete
        product.is_active = False
        await db.commit()

        return {"message": "ลบสินค้าเรียบร้อย"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error deleting product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

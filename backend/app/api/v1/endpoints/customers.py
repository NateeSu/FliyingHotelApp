"""
Customer API Endpoints (Phase 4)
Handles customer management and search
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.models import User
from app.services import CustomerService
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerSearchResult,
    CustomerListResponse
)

router = APIRouter()


@router.get("/search", response_model=List[CustomerSearchResult])
async def search_customers(
    q: str = Query(..., min_length=1, max_length=100, description="Search query (name or phone)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search customers by name or phone number (autocomplete)

    Requires authentication.

    Query Parameters:
        - q: Search query string
        - limit: Maximum number of results (default: 10, max: 50)

    Returns:
        List of matching customers (sorted by most recent visit)
    """
    service = CustomerService(db)
    customers = await service.search_customers(query=q, limit=limit)

    return [CustomerSearchResult.model_validate(c) for c in customers]


@router.get("/", response_model=CustomerListResponse)
async def get_customers(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of customers"),
    offset: int = Query(0, ge=0, description="Number of customers to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all customers with pagination

    Requires authentication.

    Query Parameters:
        - limit: Maximum number of customers (default: 100, max: 500)
        - offset: Number of customers to skip (default: 0)

    Returns:
        List of customers with total count
    """
    service = CustomerService(db)
    customers, total = await service.get_all_customers(limit=limit, offset=offset)

    return CustomerListResponse(
        data=[CustomerResponse.model_validate(c) for c in customers],
        total=total
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get customer by ID

    Requires authentication.

    Returns:
        Customer information
    """
    service = CustomerService(db)
    customer = await service.get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลลูกค้า")

    return CustomerResponse.model_validate(customer)


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new customer

    Requires authentication.

    Request Body:
        - full_name: Full name (required)
        - phone_number: Phone number (required, unique)
        - email: Email address (optional)
        - id_card_number: ID card number (optional)
        - address: Address (optional)
        - notes: Notes (optional)

    Returns:
        Created customer

    Raises:
        400: If customer with same phone number already exists
    """
    try:
        service = CustomerService(db)
        customer = await service.create_customer(customer_data, check_duplicate=True)
        return CustomerResponse.model_validate(customer)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update customer information

    Requires authentication.

    Returns:
        Updated customer
    """
    service = CustomerService(db)
    customer = await service.update_customer(customer_id, customer_data)

    if not customer:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลลูกค้า")

    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}/history")
async def get_customer_history(
    customer_id: int,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of check-ins to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get customer visit history

    Requires authentication.

    Query Parameters:
        - limit: Maximum number of recent check-ins (default: 10, max: 50)

    Returns:
        Customer information with visit history
    """
    service = CustomerService(db)
    history = await service.get_customer_history(customer_id, limit=limit)

    if not history:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลลูกค้า")

    return history

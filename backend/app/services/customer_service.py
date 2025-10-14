"""
Customer Service (Phase 4)
Handles customer management and search functionality
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, and_
from sqlalchemy.orm import joinedload

from app.models import Customer, CheckIn
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse


class CustomerService:
    """Service for managing customers"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_customer(
        self,
        customer_data: CustomerCreate,
        check_duplicate: bool = True
    ) -> Customer:
        """
        Create a new customer

        Args:
            customer_data: Customer data
            check_duplicate: If True, check for existing customer by phone number

        Returns:
            Created customer

        Raises:
            ValueError: If duplicate customer found (when check_duplicate=True)
        """
        if check_duplicate:
            # Check for existing customer by phone number
            existing = await self.get_customer_by_phone(customer_data.phone_number)
            if existing:
                raise ValueError(
                    f"พบข้อมูลลูกค้าที่มีเบอร์โทรศัพท์ {customer_data.phone_number} อยู่แล้ว"
                )

        customer = Customer(
            full_name=customer_data.full_name,
            phone_number=customer_data.phone_number,
            email=customer_data.email,
            id_card_number=customer_data.id_card_number,
            address=customer_data.address,
            notes=customer_data.notes
        )

        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)

        return customer

    async def get_or_create_customer(
        self,
        customer_data: CustomerCreate
    ) -> Tuple[Customer, bool]:
        """
        Get existing customer by phone or create new one

        Returns:
            Tuple of (customer, created) where created is True if new customer was created
        """
        existing = await self.get_customer_by_phone(customer_data.phone_number)

        if existing:
            # Update existing customer data if provided
            if customer_data.full_name:
                existing.full_name = customer_data.full_name
            if customer_data.email:
                existing.email = customer_data.email
            if customer_data.id_card_number:
                existing.id_card_number = customer_data.id_card_number
            if customer_data.address:
                existing.address = customer_data.address

            await self.db.commit()
            await self.db.refresh(existing)

            return existing, False

        # Create new customer
        customer = await self.create_customer(customer_data, check_duplicate=False)
        return customer, True

    async def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_customer_by_phone(self, phone_number: str) -> Optional[Customer]:
        """Get customer by phone number"""
        stmt = select(Customer).where(Customer.phone_number == phone_number)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_customers(
        self,
        query: str,
        limit: int = 10
    ) -> List[Customer]:
        """
        Search customers by name or phone number (autocomplete)

        Args:
            query: Search query string
            limit: Maximum number of results (default: 10)

        Returns:
            List of matching customers
        """
        # Search by name or phone number
        search_pattern = f"%{query}%"

        stmt = (
            select(Customer)
            .where(
                or_(
                    Customer.full_name.ilike(search_pattern),
                    Customer.phone_number.like(search_pattern)
                )
            )
            .order_by(Customer.last_visit_date.desc().nullslast())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_customer(
        self,
        customer_id: int,
        customer_data: CustomerUpdate
    ) -> Optional[Customer]:
        """Update customer information"""
        customer = await self.get_customer_by_id(customer_id)

        if not customer:
            return None

        # Update fields if provided
        update_data = customer_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(customer, field, value)

        await self.db.commit()
        await self.db.refresh(customer)

        return customer

    async def get_customer_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> dict:
        """
        Get customer visit history

        Returns:
            Dictionary with customer info and visit history
        """
        customer = await self.get_customer_by_id(customer_id)

        if not customer:
            return None

        # Load check-ins with relationships
        stmt = (
            select(Customer)
            .where(Customer.id == customer_id)
            .options(
                joinedload(Customer.check_ins).joinedload(CheckIn.room),
                joinedload(Customer.bookings)
            )
        )

        result = await self.db.execute(stmt)
        customer_with_relations = result.scalar_one_or_none()

        # Sort check-ins by date (most recent first)
        check_ins = sorted(
            customer_with_relations.check_ins,
            key=lambda x: x.check_in_time,
            reverse=True
        )[:limit]

        return {
            "customer": customer_with_relations,
            "total_visits": customer.total_visits,
            "total_spent": customer.total_spent,
            "last_visit_date": customer.last_visit_date,
            "recent_check_ins": check_ins
        }

    async def get_all_customers(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Customer], int]:
        """
        Get all customers with pagination

        Returns:
            Tuple of (customers, total_count)
        """
        # Get total count
        count_stmt = select(func.count()).select_from(Customer)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()

        # Get customers
        stmt = (
            select(Customer)
            .order_by(Customer.last_visit_date.desc().nullslast())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        customers = list(result.scalars().all())

        return customers, total

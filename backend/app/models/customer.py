"""
Customer Model (Phase 3 - Basic, Full implementation in Phase 4)
Mini CRM for customer data
"""
from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Customer(Base):
    """
    Customer Model
    Stores guest information for CRM purposes
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    full_name = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)  # Indexed for search and duplicate detection
    id_card_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    notes = Column(String(1000), nullable=True)

    # Visit tracking
    first_visit_date = Column(Date, nullable=True)
    last_visit_date = Column(Date, nullable=True)
    total_visits = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = relationship("Booking", back_populates="customer")
    check_ins = relationship("CheckIn", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.full_name}, phone={self.phone_number})>"

"""
Payment Model (Phase 4)
Stores payment records for check-ins
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Payment(Base):
    """Payment Model - Records payments for check-ins"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    check_in_id = Column(Integer, ForeignKey("check_ins.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(20), nullable=False)  # CASH, BANK_TRANSFER, CREDIT_CARD, QR_CODE
    payment_time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    payment_slip_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    check_in = relationship("CheckIn", back_populates="payments")
    created_by_user = relationship("User", foreign_keys=[created_by])

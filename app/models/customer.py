from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    commerce_store_id = Column(Integer, ForeignKey("commerce_stores.id", ondelete="CASCADE"), nullable=False, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    commerce_store = relationship("CommerceStore", back_populates="customers")
    addresses = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer")


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), default="shipping", nullable=False)
    line1 = Column(String(500), nullable=False)
    line2 = Column(String(500), nullable=True)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=True)
    postal_code = Column(String(50), nullable=True)
    country = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    customer = relationship("Customer", back_populates="addresses")

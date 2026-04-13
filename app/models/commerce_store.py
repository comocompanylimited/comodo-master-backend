from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class CommerceStore(Base):
    __tablename__ = "commerce_stores"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    business = relationship("Business", back_populates="commerce_stores")
    websites = relationship("Website", back_populates="commerce_store")
    mobile_apps = relationship("MobileApp", back_populates="commerce_store")
    categories = relationship("Category", back_populates="commerce_store", cascade="all, delete-orphan")
    brands = relationship("Brand", back_populates="commerce_store", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="commerce_store", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="commerce_store", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="commerce_store", cascade="all, delete-orphan")
    discounts = relationship("Discount", back_populates="commerce_store", cascade="all, delete-orphan")
    import_jobs = relationship("ImportJob", back_populates="commerce_store", cascade="all, delete-orphan")

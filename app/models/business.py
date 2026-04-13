from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    subtitle = Column(String(500), nullable=True)
    business_type = Column(String(100), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    region = Column(String(100), nullable=True)
    owner_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    websites = relationship("Website", back_populates="business", cascade="all, delete-orphan")
    mobile_apps = relationship("MobileApp", back_populates="business", cascade="all, delete-orphan")
    commerce_stores = relationship("CommerceStore", back_populates="business", cascade="all, delete-orphan")

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class MobileApp(Base):
    __tablename__ = "mobile_apps"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    app_type = Column(String(100), nullable=True)
    platform = Column(String(50), nullable=True)
    version = Column(String(50), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    commerce_store_id = Column(Integer, ForeignKey("commerce_stores.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    business = relationship("Business", back_populates="mobile_apps")
    commerce_store = relationship("CommerceStore", back_populates="mobile_apps")

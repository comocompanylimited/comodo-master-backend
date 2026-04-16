from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    commerce_store_id = Column(Integer, ForeignKey("commerce_stores.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    channel = Column(String(100), default="web", nullable=False, index=True)
    order_status = Column(String(50), default="pending", nullable=False, index=True)
    payment_status = Column(String(50), default="pending", nullable=False, index=True)
    fulfillment_status = Column(String(50), default="unfulfilled", nullable=False, index=True)
    subtotal = Column(Numeric(12, 2), nullable=False, default=0)
    discount_total = Column(Numeric(12, 2), nullable=False, default=0)
    shipping_total = Column(Numeric(12, 2), nullable=False, default=0)
    tax_total = Column(Numeric(12, 2), nullable=False, default=0)
    total = Column(Numeric(12, 2), nullable=False, default=0)
    notes = Column(Text, nullable=True)
    customer_name = Column(String(255), nullable=True)
    customer_email = Column(String(255), nullable=True, index=True)
    customer_phone = Column(String(50), nullable=True)
    shipping_address = Column(String(500), nullable=True)
    shipping_address2 = Column(String(500), nullable=True)
    shipping_city = Column(String(255), nullable=True)
    shipping_postcode = Column(String(50), nullable=True)
    shipping_country = Column(String(100), nullable=True)
    stripe_session_id = Column(String(500), unique=True, nullable=True, index=True)
    stripe_payment_intent_id = Column(String(500), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    commerce_store = relationship("CommerceStore", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True, index=True)
    product_name = Column(String(500), nullable=False)
    sku = Column(String(255), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(12, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("ProductVariant", back_populates="order_items")

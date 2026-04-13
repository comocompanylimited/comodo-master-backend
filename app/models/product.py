from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    commerce_store_id = Column(Integer, ForeignKey("commerce_stores.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), nullable=False, index=True)
    short_description = Column(String(1000), nullable=True)
    description = Column(Text, nullable=True)
    sku = Column(String(255), unique=True, nullable=False, index=True)
    barcode = Column(String(255), nullable=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    sale_price = Column(Numeric(12, 2), nullable=True)
    compare_at_price = Column(Numeric(12, 2), nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=True)
    status = Column(String(50), default="active", nullable=False, index=True)
    visibility = Column(String(50), default="visible", nullable=False)
    featured = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    commerce_store = relationship("CommerceStore", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.sort_order")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(1000), nullable=False)
    alt_text = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="images")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(255), unique=True, nullable=True, index=True)
    barcode = Column(String(255), nullable=True)
    price = Column(Numeric(12, 2), nullable=True)
    sale_price = Column(Numeric(12, 2), nullable=True)
    compare_at_price = Column(Numeric(12, 2), nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    product = relationship("Product", back_populates="variants")
    order_items = relationship("OrderItem", back_populates="variant")

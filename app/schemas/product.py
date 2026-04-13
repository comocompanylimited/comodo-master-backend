from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ProductImageBase(BaseModel):
    image_url: str
    alt_text: Optional[str] = None
    sort_order: int = 0


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageRead(ProductImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int


class ProductVariantBase(BaseModel):
    name: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    stock_quantity: int = 0
    status: str = "active"


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    status: Optional[str] = None


class ProductVariantRead(ProductVariantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime


class ProductBase(BaseModel):
    commerce_store_id: int
    name: str
    slug: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    sku: str
    barcode: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    price: Decimal = Decimal("0.00")
    sale_price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    stock_quantity: int = 0
    low_stock_threshold: Optional[int] = None
    status: str = "active"
    visibility: str = "visible"
    featured: bool = False


class ProductCreate(ProductBase):
    images: Optional[List[ProductImageCreate]] = []
    variants: Optional[List[ProductVariantCreate]] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    barcode: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    featured: Optional[bool] = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    images: List[ProductImageRead] = []
    variants: List[ProductVariantRead] = []
    created_at: datetime
    updated_at: datetime

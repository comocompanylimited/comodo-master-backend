from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class OrderItemBase(BaseModel):
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    product_name: str
    sku: Optional[str] = None
    quantity: int = 1
    unit_price: Decimal
    line_total: Decimal


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int


class OrderBase(BaseModel):
    commerce_store_id: int
    customer_id: Optional[int] = None
    order_number: str
    channel: str = "web"
    order_status: str = "pending"
    payment_status: str = "pending"
    fulfillment_status: str = "unfulfilled"
    subtotal: Decimal = Decimal("0.00")
    discount_total: Decimal = Decimal("0.00")
    shipping_total: Decimal = Decimal("0.00")
    tax_total: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = []


class OrderUpdate(BaseModel):
    order_status: Optional[str] = None
    payment_status: Optional[str] = None
    fulfillment_status: Optional[str] = None
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    order_status: str


class PaymentStatusUpdate(BaseModel):
    payment_status: str


class FulfillmentStatusUpdate(BaseModel):
    fulfillment_status: str


class OrderRead(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    items: List[OrderItemRead] = []
    created_at: datetime
    updated_at: datetime

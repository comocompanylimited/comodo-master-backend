from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DiscountBase(BaseModel):
    commerce_store_id: int
    name: str
    code: Optional[str] = None
    discount_type: str
    value: Decimal
    status: str = "active"
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    usage_limit: Optional[int] = None


class DiscountCreate(DiscountBase):
    pass


class DiscountUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    discount_type: Optional[str] = None
    value: Optional[Decimal] = None
    status: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    usage_limit: Optional[int] = None


class DiscountRead(DiscountBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerAddressBase(BaseModel):
    type: str = "shipping"
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str
    is_default: bool = False


class CustomerAddressCreate(CustomerAddressBase):
    pass


class CustomerAddressUpdate(BaseModel):
    type: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None


class CustomerAddressRead(CustomerAddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int


class CustomerBase(BaseModel):
    commerce_store_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    status: str = "active"


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    addresses: List[CustomerAddressRead] = []
    created_at: datetime
    updated_at: datetime

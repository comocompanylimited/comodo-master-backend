from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BusinessBase(BaseModel):
    name: str
    subtitle: Optional[str] = None
    business_type: Optional[str] = None
    status: str = "active"
    region: Optional[str] = None
    owner_name: Optional[str] = None


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    subtitle: Optional[str] = None
    business_type: Optional[str] = None
    status: Optional[str] = None
    region: Optional[str] = None
    owner_name: Optional[str] = None


class BusinessRead(BusinessBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

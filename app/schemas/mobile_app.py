from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MobileAppBase(BaseModel):
    name: str
    business_id: int
    app_type: Optional[str] = None
    platform: Optional[str] = None
    version: Optional[str] = None
    status: str = "active"
    commerce_store_id: Optional[int] = None


class MobileAppCreate(MobileAppBase):
    pass


class MobileAppUpdate(BaseModel):
    name: Optional[str] = None
    app_type: Optional[str] = None
    platform: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    commerce_store_id: Optional[int] = None


class MobileAppRead(MobileAppBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

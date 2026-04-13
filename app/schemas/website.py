from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class WebsiteBase(BaseModel):
    name: str
    business_id: int
    website_type: Optional[str] = None
    domain: Optional[str] = None
    environment: Optional[str] = "production"
    status: str = "active"
    commerce_store_id: Optional[int] = None


class WebsiteCreate(WebsiteBase):
    pass


class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    website_type: Optional[str] = None
    domain: Optional[str] = None
    environment: Optional[str] = None
    status: Optional[str] = None
    commerce_store_id: Optional[int] = None


class WebsiteRead(WebsiteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

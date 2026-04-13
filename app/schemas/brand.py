from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BrandBase(BaseModel):
    name: str
    commerce_store_id: int
    slug: str
    description: Optional[str] = None
    status: str = "active"


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class BrandRead(BrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

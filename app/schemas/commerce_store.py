from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CommerceStoreBase(BaseModel):
    name: str
    business_id: int
    status: str = "active"


class CommerceStoreCreate(CommerceStoreBase):
    pass


class CommerceStoreUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None


class CommerceStoreRead(CommerceStoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

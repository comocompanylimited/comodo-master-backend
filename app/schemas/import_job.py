from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ImportJobBase(BaseModel):
    commerce_store_id: int
    file_name: str
    status: str = "pending"
    total_rows: int = 0
    created_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0


class ImportJobCreate(ImportJobBase):
    pass


class ImportJobRead(ImportJobBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

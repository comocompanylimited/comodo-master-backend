from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

DataT = TypeVar("DataT")


class PaginatedResponse(BaseModel, Generic[DataT]):
    total: int
    page: int
    page_size: int
    results: List[DataT]


class MessageResponse(BaseModel):
    message: str

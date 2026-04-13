from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.commerce_store import CommerceStore
from app.schemas.commerce_store import CommerceStoreCreate, CommerceStoreUpdate


class CRUDCommerceStore(CRUDBase[CommerceStore, CommerceStoreCreate, CommerceStoreUpdate]):
    def get_by_business(self, db: Session, *, business_id: int, skip: int = 0, limit: int = 50) -> List[CommerceStore]:
        return db.query(CommerceStore).filter(CommerceStore.business_id == business_id).offset(skip).limit(limit).all()


crud_commerce_store = CRUDCommerceStore(CommerceStore)

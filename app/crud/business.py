from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessUpdate


class CRUDBusiness(CRUDBase[Business, BusinessCreate, BusinessUpdate]):
    def get_multi_filtered(
        self,
        db: Session,
        *,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Business]:
        q = db.query(Business)
        if status:
            q = q.filter(Business.status == status)
        return q.offset(skip).limit(limit).all()

    def count_filtered(self, db: Session, *, status: Optional[str] = None) -> int:
        q = db.query(Business)
        if status:
            q = q.filter(Business.status == status)
        return q.count()


crud_business = CRUDBusiness(Business)

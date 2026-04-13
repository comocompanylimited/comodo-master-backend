from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.discount import Discount
from app.schemas.discount import DiscountCreate, DiscountUpdate


class CRUDDiscount(CRUDBase[Discount, DiscountCreate, DiscountUpdate]):
    def get_by_store(
        self,
        db: Session,
        *,
        commerce_store_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Discount]:
        q = db.query(Discount).filter(Discount.commerce_store_id == commerce_store_id)
        if status:
            q = q.filter(Discount.status == status)
        return q.order_by(Discount.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_code(self, db: Session, *, commerce_store_id: int, code: str) -> Optional[Discount]:
        return db.query(Discount).filter(
            Discount.commerce_store_id == commerce_store_id,
            Discount.code == code,
        ).first()

    def count_by_store(self, db: Session, *, commerce_store_id: int) -> int:
        return db.query(Discount).filter(Discount.commerce_store_id == commerce_store_id).count()


crud_discount = CRUDDiscount(Discount)

from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandUpdate


class CRUDBrand(CRUDBase[Brand, BrandCreate, BrandUpdate]):
    def get_by_store(
        self,
        db: Session,
        *,
        commerce_store_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Brand]:
        q = db.query(Brand).filter(Brand.commerce_store_id == commerce_store_id)
        if status:
            q = q.filter(Brand.status == status)
        return q.offset(skip).limit(limit).all()

    def get_by_slug(self, db: Session, *, commerce_store_id: int, slug: str) -> Optional[Brand]:
        return db.query(Brand).filter(
            Brand.commerce_store_id == commerce_store_id,
            Brand.slug == slug,
        ).first()

    def count_by_store(self, db: Session, *, commerce_store_id: int) -> int:
        return db.query(Brand).filter(Brand.commerce_store_id == commerce_store_id).count()


crud_brand = CRUDBrand(Brand)

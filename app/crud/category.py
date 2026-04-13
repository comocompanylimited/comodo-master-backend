from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_store(
        self,
        db: Session,
        *,
        commerce_store_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Category]:
        q = db.query(Category).filter(Category.commerce_store_id == commerce_store_id)
        if status:
            q = q.filter(Category.status == status)
        return q.offset(skip).limit(limit).all()

    def get_by_slug(self, db: Session, *, commerce_store_id: int, slug: str) -> Optional[Category]:
        return db.query(Category).filter(
            Category.commerce_store_id == commerce_store_id,
            Category.slug == slug,
        ).first()

    def count_by_store(self, db: Session, *, commerce_store_id: int) -> int:
        return db.query(Category).filter(Category.commerce_store_id == commerce_store_id).count()


crud_category = CRUDCategory(Category)

from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.website import Website
from app.schemas.website import WebsiteCreate, WebsiteUpdate


class CRUDWebsite(CRUDBase[Website, WebsiteCreate, WebsiteUpdate]):
    def get_by_business(self, db: Session, *, business_id: int, skip: int = 0, limit: int = 50) -> List[Website]:
        return db.query(Website).filter(Website.business_id == business_id).offset(skip).limit(limit).all()

    def get_by_commerce_store(self, db: Session, *, commerce_store_id: int) -> List[Website]:
        return db.query(Website).filter(Website.commerce_store_id == commerce_store_id).all()


crud_website = CRUDWebsite(Website)

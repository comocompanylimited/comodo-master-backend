from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.mobile_app import MobileApp
from app.schemas.mobile_app import MobileAppCreate, MobileAppUpdate


class CRUDMobileApp(CRUDBase[MobileApp, MobileAppCreate, MobileAppUpdate]):
    def get_by_business(self, db: Session, *, business_id: int, skip: int = 0, limit: int = 50) -> List[MobileApp]:
        return db.query(MobileApp).filter(MobileApp.business_id == business_id).offset(skip).limit(limit).all()

    def get_by_commerce_store(self, db: Session, *, commerce_store_id: int) -> List[MobileApp]:
        return db.query(MobileApp).filter(MobileApp.commerce_store_id == commerce_store_id).all()


crud_mobile_app = CRUDMobileApp(MobileApp)

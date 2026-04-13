from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.customer import Customer, CustomerAddress
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerAddressCreate, CustomerAddressUpdate


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def get_multi_filtered(
        self,
        db: Session,
        *,
        commerce_store_id: int,
        status: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Customer]:
        q = db.query(Customer).filter(Customer.commerce_store_id == commerce_store_id)
        if status:
            q = q.filter(Customer.status == status)
        if search:
            q = q.filter(
                (Customer.first_name.ilike(f"%{search}%"))
                | (Customer.last_name.ilike(f"%{search}%"))
                | (Customer.email.ilike(f"%{search}%"))
            )
        return q.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()

    def count_filtered(
        self, db: Session, *, commerce_store_id: int, status: Optional[str] = None, search: Optional[str] = None
    ) -> int:
        q = db.query(Customer).filter(Customer.commerce_store_id == commerce_store_id)
        if status:
            q = q.filter(Customer.status == status)
        if search:
            q = q.filter(
                (Customer.first_name.ilike(f"%{search}%"))
                | (Customer.last_name.ilike(f"%{search}%"))
                | (Customer.email.ilike(f"%{search}%"))
            )
        return q.count()


class CRUDCustomerAddress(CRUDBase[CustomerAddress, CustomerAddressCreate, CustomerAddressUpdate]):
    def get_by_customer(self, db: Session, *, customer_id: int) -> List[CustomerAddress]:
        return db.query(CustomerAddress).filter(CustomerAddress.customer_id == customer_id).all()


crud_customer = CRUDCustomer(Customer)
crud_customer_address = CRUDCustomerAddress(CustomerAddress)

from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.crud.base import CRUDBase
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def create(self, db: Session, *, obj_in: OrderCreate) -> Order:
        data = obj_in.model_dump(exclude={"items"})
        db_obj = Order(**data)
        db.add(db_obj)
        db.flush()
        for item in (obj_in.items or []):
            db.add(OrderItem(order_id=db_obj.id, **item.model_dump()))
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_filtered(
        self,
        db: Session,
        *,
        commerce_store_id: int,
        order_status: Optional[str] = None,
        payment_status: Optional[str] = None,
        fulfillment_status: Optional[str] = None,
        channel: Optional[str] = None,
        customer_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Order]:
        q = db.query(Order).filter(Order.commerce_store_id == commerce_store_id)
        if order_status:
            q = q.filter(Order.order_status == order_status)
        if payment_status:
            q = q.filter(Order.payment_status == payment_status)
        if fulfillment_status:
            q = q.filter(Order.fulfillment_status == fulfillment_status)
        if channel:
            q = q.filter(Order.channel == channel)
        if customer_id is not None:
            q = q.filter(Order.customer_id == customer_id)
        return q.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    def count_filtered(
        self,
        db: Session,
        *,
        commerce_store_id: int,
        order_status: Optional[str] = None,
        payment_status: Optional[str] = None,
        fulfillment_status: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> int:
        q = db.query(Order).filter(Order.commerce_store_id == commerce_store_id)
        if order_status:
            q = q.filter(Order.order_status == order_status)
        if payment_status:
            q = q.filter(Order.payment_status == payment_status)
        if fulfillment_status:
            q = q.filter(Order.fulfillment_status == fulfillment_status)
        if channel:
            q = q.filter(Order.channel == channel)
        return q.count()

    def get_total_revenue(self, db: Session, *, commerce_store_id: int) -> Decimal:
        result = db.query(func.sum(Order.total)).filter(
            Order.commerce_store_id == commerce_store_id,
            Order.payment_status == "paid",
        ).scalar()
        return result or Decimal("0.00")

    def get_recent(self, db: Session, *, commerce_store_id: int, limit: int = 10) -> List[Order]:
        return db.query(Order).filter(
            Order.commerce_store_id == commerce_store_id
        ).order_by(Order.created_at.desc()).limit(limit).all()


crud_order = CRUDOrder(Order)

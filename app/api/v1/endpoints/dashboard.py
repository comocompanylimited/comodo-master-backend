from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.deps import get_db, get_current_active_user
from app.crud.order import crud_order
from app.crud.product import crud_product
from app.crud.customer import crud_customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderRead

router = APIRouter()


class DashboardSummary(BaseModel):
    total_revenue: Decimal
    total_orders: int
    total_customers: int
    total_products: int
    low_stock_count: int


class TopProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    total_sold: int
    total_revenue: Decimal


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    commerce_store_id: int = Query(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    total_revenue = crud_order.get_total_revenue(db, commerce_store_id=commerce_store_id)
    total_orders = crud_order.count_filtered(db, commerce_store_id=commerce_store_id)
    total_customers = crud_customer.count_filtered(db, commerce_store_id=commerce_store_id)
    total_products = crud_product.count_filtered(db, commerce_store_id=commerce_store_id)
    low_stock = crud_product.count_low_stock(db, commerce_store_id=commerce_store_id)

    return DashboardSummary(
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_customers=total_customers,
        total_products=total_products,
        low_stock_count=low_stock,
    )


@router.get("/recent-orders", response_model=List[OrderRead])
def get_recent_orders(
    commerce_store_id: int = Query(...),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    return crud_order.get_recent(db, commerce_store_id=commerce_store_id, limit=limit)


@router.get("/top-products", response_model=List[TopProduct])
def get_top_products(
    commerce_store_id: int = Query(...),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    results = (
        db.query(
            OrderItem.product_id,
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.line_total).label("total_revenue"),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.commerce_store_id == commerce_store_id)
        .filter(OrderItem.product_id.isnot(None))
        .group_by(OrderItem.product_id, OrderItem.product_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )
    return [
        TopProduct(
            product_id=r.product_id,
            product_name=r.product_name,
            total_sold=r.total_sold or 0,
            total_revenue=r.total_revenue or Decimal("0.00"),
        )
        for r in results
    ]

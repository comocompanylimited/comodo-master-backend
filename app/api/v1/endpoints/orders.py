from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.order import crud_order
from app.schemas.order import (
    OrderCreate, OrderRead, OrderUpdate,
    OrderStatusUpdate, PaymentStatusUpdate, FulfillmentStatusUpdate,
)
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[OrderRead])
def list_orders(
    commerce_store_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    order_status: Optional[str] = None,
    payment_status: Optional[str] = None,
    fulfillment_status: Optional[str] = None,
    channel: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    total = crud_order.count_filtered(
        db, commerce_store_id=commerce_store_id, order_status=order_status,
        payment_status=payment_status, fulfillment_status=fulfillment_status, channel=channel,
    )
    items = crud_order.get_multi_filtered(
        db, commerce_store_id=commerce_store_id, order_status=order_status,
        payment_status=payment_status, fulfillment_status=fulfillment_status,
        channel=channel, customer_id=customer_id, skip=skip, limit=limit,
    )
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=OrderRead, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_order.create(db, obj_in=payload)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_order.get(db, id=order_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Order not found")
    return obj


@router.patch("/{order_id}", response_model=OrderRead)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_order.get(db, id=order_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud_order.update(db, db_obj=obj, obj_in=payload)


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_order.get(db, id=order_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud_order.update(db, db_obj=obj, obj_in={"order_status": payload.order_status})


@router.patch("/{order_id}/payment-status", response_model=OrderRead)
def update_payment_status(order_id: int, payload: PaymentStatusUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_order.get(db, id=order_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud_order.update(db, db_obj=obj, obj_in={"payment_status": payload.payment_status})


@router.patch("/{order_id}/fulfillment-status", response_model=OrderRead)
def update_fulfillment_status(order_id: int, payload: FulfillmentStatusUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_order.get(db, id=order_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud_order.update(db, db_obj=obj, obj_in={"fulfillment_status": payload.fulfillment_status})


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_order.get(db, id=order_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Order not found")
    crud_order.remove(db, id=order_id)

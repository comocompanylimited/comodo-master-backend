from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.discount import crud_discount
from app.schemas.discount import DiscountCreate, DiscountRead, DiscountUpdate
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DiscountRead])
def list_discounts(
    commerce_store_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    total = crud_discount.count_by_store(db, commerce_store_id=commerce_store_id)
    items = crud_discount.get_by_store(db, commerce_store_id=commerce_store_id, status=status, skip=skip, limit=limit)
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=DiscountRead, status_code=201)
def create_discount(payload: DiscountCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_discount.create(db, obj_in=payload)


@router.get("/{discount_id}", response_model=DiscountRead)
def get_discount(discount_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_discount.get(db, id=discount_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Discount not found")
    return obj


@router.patch("/{discount_id}", response_model=DiscountRead)
def update_discount(discount_id: int, payload: DiscountUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_discount.get(db, id=discount_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Discount not found")
    return crud_discount.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{discount_id}", status_code=204)
def delete_discount(discount_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_discount.get(db, id=discount_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Discount not found")
    crud_discount.remove(db, id=discount_id)

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.business import crud_business
from app.schemas.business import BusinessCreate, BusinessRead, BusinessUpdate
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[BusinessRead])
def list_businesses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    total = crud_business.count_filtered(db, status=status)
    items = crud_business.get_multi_filtered(db, status=status, skip=skip, limit=limit)
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=BusinessRead, status_code=201)
def create_business(
    payload: BusinessCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    return crud_business.create(db, obj_in=payload)


@router.get("/{business_id}", response_model=BusinessRead)
def get_business(business_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_business.get(db, id=business_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Business not found")
    return obj


@router.patch("/{business_id}", response_model=BusinessRead)
def update_business(
    business_id: int,
    payload: BusinessUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    obj = crud_business.get(db, id=business_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Business not found")
    return crud_business.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{business_id}", status_code=204)
def delete_business(business_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_business.get(db, id=business_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Business not found")
    crud_business.remove(db, id=business_id)

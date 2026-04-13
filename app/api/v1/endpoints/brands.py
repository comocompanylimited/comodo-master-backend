from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.brand import crud_brand
from app.schemas.brand import BrandCreate, BrandRead, BrandUpdate
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[BrandRead])
def list_brands(
    commerce_store_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    total = crud_brand.count_by_store(db, commerce_store_id=commerce_store_id)
    items = crud_brand.get_by_store(db, commerce_store_id=commerce_store_id, status=status, skip=skip, limit=limit)
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=BrandRead, status_code=201)
def create_brand(payload: BrandCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_brand.create(db, obj_in=payload)


@router.get("/{brand_id}", response_model=BrandRead)
def get_brand(brand_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_brand.get(db, id=brand_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Brand not found")
    return obj


@router.patch("/{brand_id}", response_model=BrandRead)
def update_brand(brand_id: int, payload: BrandUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_brand.get(db, id=brand_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Brand not found")
    return crud_brand.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{brand_id}", status_code=204)
def delete_brand(brand_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_brand.get(db, id=brand_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Brand not found")
    crud_brand.remove(db, id=brand_id)

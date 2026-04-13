from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.commerce_store import crud_commerce_store
from app.schemas.commerce_store import CommerceStoreCreate, CommerceStoreRead, CommerceStoreUpdate
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CommerceStoreRead])
def list_commerce_stores(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    business_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    if business_id:
        items = crud_commerce_store.get_by_business(db, business_id=business_id, skip=skip, limit=limit)
        total = len(items)
    else:
        total = crud_commerce_store.count(db)
        items = crud_commerce_store.get_multi(db, skip=skip, limit=limit)
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=CommerceStoreRead, status_code=201)
def create_commerce_store(payload: CommerceStoreCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_commerce_store.create(db, obj_in=payload)


@router.get("/{store_id}", response_model=CommerceStoreRead)
def get_commerce_store(store_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_commerce_store.get(db, id=store_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Commerce store not found")
    return obj


@router.patch("/{store_id}", response_model=CommerceStoreRead)
def update_commerce_store(store_id: int, payload: CommerceStoreUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_commerce_store.get(db, id=store_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Commerce store not found")
    return crud_commerce_store.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{store_id}", status_code=204)
def delete_commerce_store(store_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_commerce_store.get(db, id=store_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Commerce store not found")
    crud_commerce_store.remove(db, id=store_id)

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.category import crud_category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CategoryRead])
def list_categories(
    commerce_store_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    total = crud_category.count_by_store(db, commerce_store_id=commerce_store_id)
    items = crud_category.get_by_store(db, commerce_store_id=commerce_store_id, status=status, skip=skip, limit=limit)
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_category.create(db, obj_in=payload)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_category.get(db, id=category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return obj


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_category.get(db, id=category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud_category.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_category.get(db, id=category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    crud_category.remove(db, id=category_id)

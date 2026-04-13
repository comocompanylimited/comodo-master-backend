from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.mobile_app import crud_mobile_app
from app.schemas.mobile_app import MobileAppCreate, MobileAppRead, MobileAppUpdate
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[MobileAppRead])
def list_mobile_apps(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    business_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    if business_id:
        items = crud_mobile_app.get_by_business(db, business_id=business_id, skip=skip, limit=limit)
        total = len(items)
    else:
        total = crud_mobile_app.count(db)
        items = crud_mobile_app.get_multi(db, skip=skip, limit=limit)
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=MobileAppRead, status_code=201)
def create_mobile_app(payload: MobileAppCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_mobile_app.create(db, obj_in=payload)


@router.get("/{app_id}", response_model=MobileAppRead)
def get_mobile_app(app_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_mobile_app.get(db, id=app_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Mobile app not found")
    return obj


@router.patch("/{app_id}", response_model=MobileAppRead)
def update_mobile_app(app_id: int, payload: MobileAppUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_mobile_app.get(db, id=app_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Mobile app not found")
    return crud_mobile_app.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{app_id}", status_code=204)
def delete_mobile_app(app_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_mobile_app.get(db, id=app_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Mobile app not found")
    crud_mobile_app.remove(db, id=app_id)

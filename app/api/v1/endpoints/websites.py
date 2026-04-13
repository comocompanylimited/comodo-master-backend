from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.website import crud_website
from app.schemas.website import WebsiteCreate, WebsiteRead, WebsiteUpdate
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[WebsiteRead])
def list_websites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    business_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    if business_id:
        items = crud_website.get_by_business(db, business_id=business_id, skip=skip, limit=limit)
        total = len(items)
    else:
        total = crud_website.count(db)
        items = crud_website.get_multi(db, skip=skip, limit=limit)
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=WebsiteRead, status_code=201)
def create_website(payload: WebsiteCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_website.create(db, obj_in=payload)


@router.get("/{website_id}", response_model=WebsiteRead)
def get_website(website_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_website.get(db, id=website_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Website not found")
    return obj


@router.patch("/{website_id}", response_model=WebsiteRead)
def update_website(website_id: int, payload: WebsiteUpdate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_website.get(db, id=website_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Website not found")
    return crud_website.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{website_id}", status_code=204)
def delete_website(website_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_website.get(db, id=website_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Website not found")
    crud_website.remove(db, id=website_id)

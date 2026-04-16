from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.crud.product import crud_product
from app.schemas.product import ProductRead
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params
import os

router = APIRouter()

DEFAULT_STORE_ID = int(os.environ.get("DEFAULT_COMMERCE_STORE_ID", "1"))


@router.get("", response_model=PaginatedResponse[ProductRead])
def list_public_products(
    commerce_store_id: int = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    featured: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    store_id = commerce_store_id or DEFAULT_STORE_ID
    skip, limit = pagination_params(page, page_size)
    total = crud_product.count_filtered(
        db, commerce_store_id=store_id, category_id=category_id,
        brand_id=brand_id, status="active", featured=featured, search=search,
    )
    items = crud_product.get_multi_filtered(
        db, commerce_store_id=store_id, category_id=category_id,
        brand_id=brand_id, status="active", featured=featured, search=search,
        skip=skip, limit=limit,
    )
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.get("/{slug}", response_model=ProductRead)
def get_public_product_by_slug(slug: str, db: Session = Depends(get_db)):
    from app.models.product import Product
    obj = db.query(Product).filter(
        Product.slug == slug,
        Product.status == "active",
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj

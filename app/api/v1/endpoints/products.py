from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.product import crud_product, crud_product_variant
from app.schemas.product import (
    ProductCreate, ProductRead, ProductUpdate,
    ProductVariantCreate, ProductVariantRead, ProductVariantUpdate,
)
from app.schemas.common import PaginatedResponse
from app.utils.pagination import pagination_params

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ProductRead])
def list_products(
    commerce_store_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    status: Optional[str] = None,
    featured: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    skip, limit = pagination_params(page, page_size)
    total = crud_product.count_filtered(
        db, commerce_store_id=commerce_store_id, category_id=category_id,
        brand_id=brand_id, status=status, featured=featured, search=search,
    )
    items = crud_product.get_multi_filtered(
        db, commerce_store_id=commerce_store_id, category_id=category_id,
        brand_id=brand_id, status=status, featured=featured, search=search,
        skip=skip, limit=limit,
    )
    return PaginatedResponse(total=total, page=page, page_size=limit, results=items)


@router.post("", response_model=ProductRead, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_product.create(db, obj_in=payload)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_product.get(db, id=product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int, payload: ProductUpdate,
    db: Session = Depends(get_db), _=Depends(get_current_active_user),
):
    obj = crud_product.get(db, id=product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud_product.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_product.get(db, id=product_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Product not found")
    crud_product.remove(db, id=product_id)


@router.get("/{product_id}/variants", response_model=list[ProductVariantRead])
def list_variants(product_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return crud_product_variant.get_by_product(db, product_id=product_id)


@router.post("/{product_id}/variants", response_model=ProductVariantRead, status_code=201)
def create_variant(
    product_id: int, payload: ProductVariantCreate,
    db: Session = Depends(get_db), _=Depends(get_current_active_user),
):
    from app.models.product import ProductVariant
    obj = ProductVariant(product_id=product_id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{product_id}/variants/{variant_id}", response_model=ProductVariantRead)
def update_variant(
    product_id: int, variant_id: int, payload: ProductVariantUpdate,
    db: Session = Depends(get_db), _=Depends(get_current_active_user),
):
    obj = crud_product_variant.get(db, id=variant_id)
    if not obj or obj.product_id != product_id:
        raise HTTPException(status_code=404, detail="Variant not found")
    return crud_product_variant.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{product_id}/variants/{variant_id}", status_code=204)
def delete_variant(
    product_id: int, variant_id: int,
    db: Session = Depends(get_db), _=Depends(get_current_active_user),
):
    obj = crud_product_variant.get(db, id=variant_id)
    if not obj or obj.product_id != product_id:
        raise HTTPException(status_code=404, detail="Variant not found")
    crud_product_variant.remove(db, id=variant_id)

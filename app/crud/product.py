from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.product import Product, ProductImage, ProductVariant
from app.schemas.product import ProductCreate, ProductUpdate, ProductVariantCreate, ProductVariantUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def create(self, db: Session, *, obj_in: ProductCreate) -> Product:
        data = obj_in.model_dump(exclude={"images", "variants"})
        db_obj = Product(**data)
        db.add(db_obj)
        db.flush()
        for img in (obj_in.images or []):
            db.add(ProductImage(product_id=db_obj.id, **img.model_dump()))
        for var in (obj_in.variants or []):
            db.add(ProductVariant(product_id=db_obj.id, **var.model_dump()))
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_filtered(
        self,
        db: Session,
        *,
        commerce_store_id: int,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        status: Optional[str] = None,
        featured: Optional[bool] = None,
        search: Optional[str] = None,
        short_description: Optional[str] = None,
        short_description_in: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Product]:
        q = db.query(Product).filter(Product.commerce_store_id == commerce_store_id)
        if category_id is not None:
            q = q.filter(Product.category_id == category_id)
        if brand_id is not None:
            q = q.filter(Product.brand_id == brand_id)
        if status:
            q = q.filter(Product.status == status)
        if featured is not None:
            q = q.filter(Product.featured == featured)
        if search:
            q = q.filter(Product.name.ilike(f"%{search}%"))
        if short_description:
            q = q.filter(Product.short_description == short_description)
        if short_description_in:
            q = q.filter(Product.short_description.in_(short_description_in))
        return q.order_by(Product.price.desc()).offset(skip).limit(limit).all()

    def count_filtered(
        self,
        db: Session,
        *,
        commerce_store_id: int,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        status: Optional[str] = None,
        featured: Optional[bool] = None,
        search: Optional[str] = None,
        short_description: Optional[str] = None,
        short_description_in: Optional[List[str]] = None,
    ) -> int:
        q = db.query(Product).filter(Product.commerce_store_id == commerce_store_id)
        if category_id is not None:
            q = q.filter(Product.category_id == category_id)
        if brand_id is not None:
            q = q.filter(Product.brand_id == brand_id)
        if status:
            q = q.filter(Product.status == status)
        if featured is not None:
            q = q.filter(Product.featured == featured)
        if search:
            q = q.filter(Product.name.ilike(f"%{search}%"))
        if short_description:
            q = q.filter(Product.short_description == short_description)
        if short_description_in:
            q = q.filter(Product.short_description.in_(short_description_in))
        return q.count()

    def count_low_stock(self, db: Session, *, commerce_store_id: int) -> int:
        return db.query(Product).filter(
            Product.commerce_store_id == commerce_store_id,
            Product.low_stock_threshold.isnot(None),
            Product.stock_quantity <= Product.low_stock_threshold,
        ).count()


class CRUDProductVariant(CRUDBase[ProductVariant, ProductVariantCreate, ProductVariantUpdate]):
    def get_by_product(self, db: Session, *, product_id: int) -> List[ProductVariant]:
        return db.query(ProductVariant).filter(ProductVariant.product_id == product_id).all()


crud_product = CRUDProduct(Product)
crud_product_variant = CRUDProductVariant(ProductVariant)

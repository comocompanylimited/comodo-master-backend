import re
import requests
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.product import Product, ProductImage
from app.models.commerce_store import CommerceStore
from app.models.business import Business

router = APIRouter()


@router.get("/products")
def verify_products(db: Session = Depends(get_db)):
    products = db.query(Product).limit(50).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "price": float(p.price),
            "source": p.source,
            "commerce_store_id": p.commerce_store_id,
        }
        for p in products
    ]


@router.get("/commerce-stores")
def list_commerce_stores(db: Session = Depends(get_db)):
    stores = db.query(CommerceStore).all()
    created = None
    if not stores:
        business = db.query(Business).first()
        if not business:
            business = Business(name="Covora", status="active")
            db.add(business)
            db.flush()
        store = CommerceStore(business_id=business.id, name="Covora Store", status="active")
        db.add(store)
        db.commit()
        db.refresh(store)
        stores = [store]
        created = store.id
    return {
        "stores": [{"id": s.id, "name": s.name, "business_id": s.business_id} for s in stores],
        "created_store_id": created,
    }


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


def _get_access_token() -> str:
    response = requests.post(
        "https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken",
        json={"apiKey": "CJ5330994@api@87b2693dfc4d423aa432c499eab5aaa3"},
        headers={"Content-Type": "application/json"},
    )
    return response.json()["data"]["accessToken"]


@router.get("/test-token")
def get_cj_token():
    response = requests.post(
        "https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken",
        json={"apiKey": "CJ5330994@api@87b2693dfc4d423aa432c499eab5aaa3"},
        headers={"Content-Type": "application/json"},
    )
    return response.json()


@router.get("/test-products")
def get_cj_products():
    token = _get_access_token()
    response = requests.get(
        "https://developers.cjdropshipping.com/api2.0/v1/product/list",
        headers={"CJ-Access-Token": token, "Content-Type": "application/json"},
    )
    return response.json()


def _to_float(val, default=0.0):
    try:
        if val is None:
            return default
        s = str(val).strip()
        s = re.split(r"\s*[-–]+\s*", s)[0].strip()
        return float(s)
    except (TypeError, ValueError):
        return default


@router.delete("/clear-products")
def clear_cj_products(
    commerce_store_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Delete all CJ-sourced products for a store so you can reimport cleanly."""
    products = db.query(Product).filter(
        Product.commerce_store_id == commerce_store_id,
        Product.source == "cj",
    ).all()
    for p in products:
        db.delete(p)
    db.commit()
    return {"deleted_count": len(products)}


def _import_from_cj(
    token: str,
    commerce_store_id: int,
    db: Session,
    category_name: str | None = None,
    page_num: int = 1,
    page_size: int = 50,
) -> tuple[int, int, int, list]:
    """Fetch one page from CJ and save new products. Returns (imported, skipped, failed, errors)."""
    params: dict = {"pageNum": page_num, "pageSize": page_size}
    if category_name:
        params["categoryName"] = category_name

    response = requests.get(
        "https://developers.cjdropshipping.com/api2.0/v1/product/list",
        headers={"CJ-Access-Token": token, "Content-Type": "application/json"},
        params=params,
    )
    data = response.json()
    products_raw = (data.get("data") or {}).get("list") or []

    imported = skipped = failed = 0
    errors: list = []

    for p in products_raw:
        sku = str(p.get("productSku") or "").strip()
        if not sku:
            skipped += 1
            continue

        try:
            if db.query(Product).filter(Product.sku == sku).first():
                skipped += 1
                continue

            name = str(p.get("productNameEn") or p.get("productName") or sku).strip()[:499]
            slug = _slugify(name) or sku.lower()
            base_slug = slug[:490]
            slug = base_slug
            i = 1
            while db.query(Product).filter(Product.slug == slug).first():
                slug = f"{base_slug}-{i}"
                i += 1

            price = _to_float(p.get("sellPrice"))
            weight = _to_float(p.get("productWeight"))

            description = p.get("remark") or None
            if description:
                description = str(description)[:5000]

            short_desc = p.get("categoryName") or category_name or None
            if short_desc:
                short_desc = str(short_desc)[:999]

            product = Product(
                commerce_store_id=commerce_store_id,
                name=name,
                slug=slug,
                sku=sku,
                price=price,
                description=description,
                short_description=short_desc,
                weight=weight,
                source="cj",
                status="active",
                visibility="visible",
                stock_quantity=0,
            )
            db.add(product)
            db.flush()

            image_url = p.get("productImage")
            if image_url:
                db.add(ProductImage(product_id=product.id, image_url=str(image_url)[:999], sort_order=0))

            db.commit()
            imported += 1

        except Exception as e:
            db.rollback()
            failed += 1
            if len(errors) < 5:
                errors.append({"sku": sku, "error": str(e)})

    return imported, skipped, failed, errors


# Women's fashion category names as used by CJ Dropshipping
WOMENS_CATEGORIES = [
    "Women's Clothing",
    "Women's Dresses",
    "Women's Tops & Tees",
    "Women's Blouses & Shirts",
    "Women's Skirts",
    "Women's Pants & Capris",
    "Women's Shorts",
    "Women's Jackets & Coats",
    "Women's Sweaters",
    "Women's Activewear",
    "Women's Sleepwear",
    "Women's Intimates",
    "Women's Swimwear",
    "Women's Shoes",
    "Women's Bags & Handbags",
    "Women's Jewelry",
    "Women's Accessories",
    "Women's Scarves & Wraps",
    "Women's Hats & Caps",
    "Women's Sunglasses",
]


@router.post("/import-products")
def import_cj_products(
    commerce_store_id: int = Query(...),
    category_name: str | None = Query(None, description="CJ category name to filter by"),
    page_num: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    imported_count = 0
    skipped_count = 0
    failed_count = 0
    errors: list = []
    fatal_error = None

    try:
        token = _get_access_token()
        imp, skip, fail, errs = _import_from_cj(
            token, commerce_store_id, db, category_name, page_num, page_size
        )
        imported_count += imp
        skipped_count += skip
        failed_count += fail
        errors.extend(errs)
    except Exception as e:
        fatal_error = str(e)

    return {
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "errors": errors,
        "fatal_error": fatal_error,
    }


@router.post("/import-womens")
def import_womens_products(
    commerce_store_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Import women's fashion products across all relevant CJ categories."""
    imported_count = 0
    skipped_count = 0
    failed_count = 0
    all_errors: list = []
    fatal_error = None

    try:
        token = _get_access_token()
        for cat in WOMENS_CATEGORIES:
            try:
                imp, skip, fail, errs = _import_from_cj(
                    token, commerce_store_id, db, category_name=cat, page_num=1, page_size=50
                )
                imported_count += imp
                skipped_count += skip
                failed_count += fail
                all_errors.extend(errs)
            except Exception as e:
                all_errors.append({"category": cat, "error": str(e)})
    except Exception as e:
        fatal_error = str(e)

    return {
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "categories_attempted": len(WOMENS_CATEGORIES),
        "errors": all_errors[:20],
        "fatal_error": fatal_error,
    }

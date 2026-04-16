import re
import requests
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.product import Product, ProductImage
from app.models.commerce_store import CommerceStore
from app.models.business import Business

router = APIRouter()

def _apply_markup(raw_price: float) -> float:
    """Under £20 CJ price → 4x markup. Over £20 → 2.4x markup."""
    markup = 4.0 if raw_price < 20.0 else 2.4
    return round(raw_price * markup, 2)

# Women's category IDs (second-level) from CJ Dropshipping taxonomy
WOMENS_CATEGORY_IDS = [
    # Women's Clothing
    {"id": "422D4713-284A-49EE-8E53-680B7DCC72FE", "name": "Tops & Sets"},
    {"id": "4257920C-6E7D-4B56-B031-0FC7AC6EF981", "name": "Bottoms"},
    {"id": "773E0DBE-EEB6-40E9-984F-4ACFB0F58C9A", "name": "Outerwear & Jackets"},
    {"id": "85CC5FF8-1CAC-4725-9F07-C778AB627E1B", "name": "Weddings & Events"},
    {"id": "23DDAF61-8F6C-40F7-9F1F-DC9BB25450B6", "name": "Accessories"},
    # Bags & Shoes
    {"id": "E93B19EF-4E2C-4526-B2DF-BBFB6F2A80A7", "name": "Women's Shoes"},
    {"id": "EC2E9303-E704-43F3-834A-A15EA653232E", "name": "Women's Luggage & Bags"},
    # Jewelry & Watches
    {"id": "123ACC01-7A11-4FB9-A532-338C0E7C04C5", "name": "Fashion Jewelry"},
    {"id": "3E53507E-2EDB-49F1-8D0D-AD01225DAD8A", "name": "Fine Jewelry"},
    {"id": "01114D8D-79BD-4AD9-85A0-72D1B050E3F8", "name": "Wedding & Engagement"},
    {"id": "F1B0B876-9103-4DF0-9EA5-524094648BFD", "name": "Women's Watches"},
    # Health, Beauty & Hair
    {"id": "6289460B-5660-468A-AE43-3D619A05AAC2", "name": "Skin Care"},
    {"id": "7EAF3E36-620B-4D78-818F-EE80955462A4", "name": "Makeup"},
    {"id": "3B5BDD4D-34F4-4807-BC6C-943C2C1BCDB8", "name": "Hair & Accessories"},
    {"id": "BF7AE6E9-E175-48FD-B1E3-3CF0126C90D0", "name": "Wigs & Extensions"},
    {"id": "CE5FADBB-B432-40B9-8B20-200F6928762A", "name": "Beauty Tools"},
    {"id": "01FD30A0-118E-4269-A6D2-8415E9C163BA", "name": "Nail Art & Tools"},
]


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


def _import_page_by_category_id(
    token: str,
    commerce_store_id: int,
    db: Session,
    category_id: str,
    category_label: str,
    page_num: int = 1,
    page_size: int = 100,
) -> tuple[int, int, int, list]:
    """Fetch one page from CJ by category ID, apply 4x markup, save new products."""
    response = requests.get(
        "https://developers.cjdropshipping.com/api2.0/v1/product/list",
        headers={"CJ-Access-Token": token, "Content-Type": "application/json"},
        params={
            "categoryId": category_id,
            "pageNum": page_num,
            "pageSize": page_size,
            "sortField": "sellPrice",
            "sortType": "DESC",
        },
        timeout=30,
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

            raw_price = _to_float(p.get("sellPrice"))
            price = _apply_markup(raw_price)

            weight = _to_float(p.get("productWeight"))

            description = p.get("remark") or None
            if description:
                description = str(description)[:5000]

            short_desc = p.get("categoryName") or category_label or None
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
                stock_quantity=999,
            )
            db.add(product)
            db.flush()

            image_url = p.get("productImage")
            if image_url:
                db.add(ProductImage(
                    product_id=product.id,
                    image_url=str(image_url)[:999],
                    sort_order=0,
                ))

            db.commit()
            imported += 1

        except Exception as e:
            db.rollback()
            failed += 1
            if len(errors) < 5:
                errors.append({"sku": sku, "error": str(e)})

    return imported, skipped, failed, errors


@router.post("/import-womens-curated")
def import_womens_curated(
    commerce_store_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Import 300 products per women's category (3 pages × 100), sorted by
    highest price descending, with 4x markup applied. ~5,100 products total.
    """
    imported_count = 0
    skipped_count = 0
    failed_count = 0
    all_errors: list = []
    fatal_error = None
    category_results = []

    try:
        token = _get_access_token()

        for cat in WOMENS_CATEGORY_IDS:
            cat_imported = 0
            cat_skipped = 0
            cat_failed = 0

            # 3 pages × 100 = 300 products per category, highest price first
            for page in range(1, 4):
                try:
                    imp, skip, fail, errs = _import_page_by_category_id(
                        token=token,
                        commerce_store_id=commerce_store_id,
                        db=db,
                        category_id=cat["id"],
                        category_label=cat["name"],
                        page_num=page,
                        page_size=100,
                    )
                    cat_imported += imp
                    cat_skipped += skip
                    cat_failed += fail
                    all_errors.extend(errs)
                except Exception as e:
                    all_errors.append({"category": cat["name"], "page": page, "error": str(e)})

            imported_count += cat_imported
            skipped_count += cat_skipped
            failed_count += cat_failed
            category_results.append({
                "category": cat["name"],
                "imported": cat_imported,
                "skipped": cat_skipped,
            })

    except Exception as e:
        fatal_error = str(e)

    return {
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "markup_applied": "4x under £20, 2.4x over £20",
        "categories": category_results,
        "errors": all_errors[:20],
        "fatal_error": fatal_error,
    }


@router.post("/import-products")
def import_cj_products(
    commerce_store_id: int = Query(...),
    category_name: str | None = Query(None),
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
        params: dict = {
            "pageNum": page_num,
            "pageSize": page_size,
            "sortField": "sellPrice",
            "sortType": "DESC",
        }
        if category_name:
            params["categoryName"] = category_name

        response = requests.get(
            "https://developers.cjdropshipping.com/api2.0/v1/product/list",
            headers={"CJ-Access-Token": token, "Content-Type": "application/json"},
            params=params,
        )
        data = response.json()
        products_raw = (data.get("data") or {}).get("list") or []

        for p in products_raw:
            sku = str(p.get("productSku") or "").strip()
            if not sku:
                skipped_count += 1
                continue
            try:
                if db.query(Product).filter(Product.sku == sku).first():
                    skipped_count += 1
                    continue

                name = str(p.get("productNameEn") or p.get("productName") or sku).strip()[:499]
                slug = _slugify(name) or sku.lower()
                base_slug = slug[:490]
                slug = base_slug
                i = 1
                while db.query(Product).filter(Product.slug == slug).first():
                    slug = f"{base_slug}-{i}"
                    i += 1

                raw_price = _to_float(p.get("sellPrice"))
                price = _apply_markup(raw_price)

                product = Product(
                    commerce_store_id=commerce_store_id,
                    name=name,
                    slug=slug,
                    sku=sku,
                    price=price,
                    description=str(p.get("remark") or "")[:5000] or None,
                    short_description=str(p.get("categoryName") or "")[:999] or None,
                    weight=_to_float(p.get("productWeight")),
                    source="cj",
                    status="active",
                    visibility="visible",
                    stock_quantity=999,
                )
                db.add(product)
                db.flush()

                image_url = p.get("productImage")
                if image_url:
                    db.add(ProductImage(product_id=product.id, image_url=str(image_url)[:999], sort_order=0))

                db.commit()
                imported_count += 1

            except Exception as e:
                db.rollback()
                failed_count += 1
                if len(errors) < 5:
                    errors.append({"sku": sku, "error": str(e)})

    except Exception as e:
        fatal_error = str(e)

    return {
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "errors": errors,
        "fatal_error": fatal_error,
    }

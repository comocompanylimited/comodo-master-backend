import re
import requests
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.product import Product, ProductImage

router = APIRouter()


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


@router.post("/import-products")
def import_cj_products(
    commerce_store_id: int = Query(...),
    db: Session = Depends(get_db),
):
    imported_count = 0
    skipped_count = 0
    failed_count = 0
    errors = []
    fatal_error = None

    try:
        token = _get_access_token()
        response = requests.get(
            "https://developers.cjdropshipping.com/api2.0/v1/product/list",
            headers={"CJ-Access-Token": token, "Content-Type": "application/json"},
        )
        data = response.json()
        products = (data.get("data") or {}).get("list") or []

        for p in products:
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

                price = _to_float(p.get("sellPrice"))
                weight = _to_float(p.get("productWeight"))

                description = p.get("remark") or None
                if description:
                    description = str(description)[:5000]

                short_desc = p.get("categoryName") or None
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

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


@router.post("/import-products")
def import_cj_products(
    commerce_store_id: int = Query(...),
    db: Session = Depends(get_db),
):
    token = _get_access_token()
    response = requests.get(
        "https://developers.cjdropshipping.com/api2.0/v1/product/list",
        headers={"CJ-Access-Token": token, "Content-Type": "application/json"},
    )
    data = response.json()
    products = (data.get("data") or {}).get("list") or []

    imported = 0
    for p in products:
        sku = p.get("productSku") or ""
        if not sku:
            continue
        if db.query(Product).filter(Product.sku == sku).first():
            continue

        name = p.get("productNameEn") or p.get("productName") or sku
        slug = _slugify(name)

        # ensure slug uniqueness
        base_slug = slug
        count = 1
        while db.query(Product).filter(Product.slug == slug).first():
            slug = f"{base_slug}-{count}"
            count += 1

        price = p.get("sellPrice") or 0

        product = Product(
            commerce_store_id=commerce_store_id,
            name=name,
            slug=slug,
            sku=sku,
            price=price,
            description=p.get("remark") or None,
            status="active",
        )
        db.add(product)
        db.flush()

        image_url = p.get("productImage")
        if image_url:
            db.add(ProductImage(product_id=product.id, image_url=image_url, sort_order=0))

        imported += 1

    db.commit()
    return {"imported": imported}

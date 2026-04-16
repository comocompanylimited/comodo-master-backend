import os
import json
import uuid
import stripe
from decimal import Decimal
from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.order import Order, OrderItem

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

FRONTEND_DOMAIN = os.environ.get("FRONTEND_URL", "https://covoralumiere.com")
DEFAULT_COMMERCE_STORE_ID = int(os.environ.get("DEFAULT_COMMERCE_STORE_ID", "1"))

router = APIRouter()


# ─── Request models ───────────────────────────────────────────────────────────

class CheckoutItem(BaseModel):
    id: str
    name: str
    slug: str = ""
    sku: str = ""
    price: float
    quantity: int
    attributes: Dict[str, Any] = {}


class CheckoutCustomer(BaseModel):
    name: str
    email: str
    phone: str = ""


class CheckoutShipping(BaseModel):
    address: str
    address2: str = ""
    city: str
    postcode: str
    country: str


class CheckoutSessionRequest(BaseModel):
    cart_items: List[CheckoutItem]
    customer: CheckoutCustomer
    shipping: CheckoutShipping
    subtotal: float = 0.0


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _safe_cart_meta(items: List[CheckoutItem]) -> str:
    data = [{"id": i.id, "name": i.name[:80], "sku": i.sku, "price": i.price, "quantity": i.quantity} for i in items]
    serialized = json.dumps(data)
    while data and len(serialized) > 499:
        data.pop()
        serialized = json.dumps(data)
    return serialized


def _serialize_order(order: Order) -> dict:
    from datetime import datetime, date
    out = {}
    for k, v in order.__dict__.items():
        if k.startswith("_"):
            continue
        if isinstance(v, Decimal):
            out[k] = float(v)
        elif isinstance(v, (datetime, date)):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


def _serialize_item(item: OrderItem) -> dict:
    from datetime import datetime, date
    out = {}
    for k, v in item.__dict__.items():
        if k.startswith("_"):
            continue
        if isinstance(v, Decimal):
            out[k] = float(v)
        elif isinstance(v, (datetime, date)):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/session", tags=["Checkout"])
def create_checkout_session(body: CheckoutSessionRequest):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured on the server.")
    if not body.cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty.")

    try:
        line_items = [
            {
                "price_data": {
                    "currency": "nzd",
                    "unit_amount": round(item.price * 100),
                    "product_data": {
                        "name": item.name,
                        "metadata": {"slug": item.slug, "sku": item.sku},
                    },
                },
                "quantity": item.quantity,
            }
            for item in body.cart_items
        ]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            customer_email=body.customer.email,
            shipping_address_collection={
                "allowed_countries": ["NZ", "AU", "GB", "US", "CA", "FR", "DE", "AE", "SG"]
            },
            metadata={
                "customer_name":     body.customer.name,
                "customer_email":    body.customer.email,
                "customer_phone":    body.customer.phone,
                "shipping_address":  body.shipping.address,
                "shipping_address2": body.shipping.address2,
                "shipping_city":     body.shipping.city,
                "shipping_postcode": body.shipping.postcode,
                "shipping_country":  body.shipping.country,
                "subtotal":          str(body.subtotal),
                "cart_items":        _safe_cart_meta(body.cart_items),
            },
            success_url=f"{FRONTEND_DOMAIN}/order-confirmation?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_DOMAIN}/checkout",
        )

        return {"url": session.url}

    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=str(getattr(e, "user_message", None) or e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/confirm", tags=["Checkout"])
def confirm_order(session_id: str = Query(...), db: Session = Depends(get_db)):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured.")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=str(getattr(e, "user_message", None) or e))

    if session.get("payment_status") != "paid":
        raise HTTPException(status_code=402, detail="Payment not completed.")

    # Return existing order if already saved
    existing = db.query(Order).filter(Order.stripe_session_id == session_id).first()
    if existing:
        return {
            "order": _serialize_order(existing),
            "items": [_serialize_item(i) for i in existing.items],
        }

    meta = session.get("metadata") or {}
    subtotal = float(meta.get("subtotal") or 0)
    total = float(session.get("amount_total") or 0) / 100

    order = Order(
        commerce_store_id=DEFAULT_COMMERCE_STORE_ID,
        order_number=f"CVR-{uuid.uuid4().hex[:8].upper()}",
        channel="web",
        order_status="pending",
        payment_status="paid",
        fulfillment_status="unfulfilled",
        subtotal=subtotal,
        total=total,
        customer_name=meta.get("customer_name", ""),
        customer_email=meta.get("customer_email") or session.get("customer_email", ""),
        customer_phone=meta.get("customer_phone", ""),
        shipping_address=meta.get("shipping_address", ""),
        shipping_address2=meta.get("shipping_address2", ""),
        shipping_city=meta.get("shipping_city", ""),
        shipping_postcode=meta.get("shipping_postcode", ""),
        shipping_country=meta.get("shipping_country", ""),
        stripe_session_id=session_id,
        stripe_payment_intent_id=session.get("payment_intent"),
    )
    db.add(order)
    db.flush()

    cart_items = []
    try:
        cart_items = json.loads(meta.get("cart_items") or "[]")
    except Exception:
        pass

    for item in cart_items:
        try:
            unit_price = float(item.get("price") or 0)
            qty = int(item.get("quantity") or 1)
            db.add(OrderItem(
                order_id=order.id,
                product_name=item.get("name", ""),
                sku=item.get("sku", ""),
                quantity=qty,
                unit_price=unit_price,
                line_total=round(unit_price * qty, 2),
            ))
        except Exception:
            pass

    db.commit()
    db.refresh(order)
    return {
        "order": _serialize_order(order),
        "items": [_serialize_item(i) for i in order.items],
    }

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

# Leaf-level CJ category IDs mapped to exact Covora nav categories.
# Using leaf IDs ensures only the correct product type is returned.
WOMENS_LEAF_CATEGORIES = [
    # ── Dresses ──────────────────────────────────────────────────────────────
    {"id": "D2432903-0D4E-4787-886F-D3D9DA7890D9", "name": "Dresses"},   # Lady Dresses
    {"id": "30E8E5CF-FBBA-48DA-84DD-E29D733089E0", "name": "Dresses"},   # Evening Dresses
    {"id": "1AFD1C87-0BB1-4BAB-AA1A-D082E767811C", "name": "Dresses"},   # Cocktail Dresses
    {"id": "88E43313-84C6-4550-B2C7-83A415AFA2DD", "name": "Dresses"},   # Prom Dresses
    {"id": "935BCF1B-5D61-422F-8439-19179FE8B492", "name": "Dresses"},   # Wedding Dresses
    {"id": "6C2516C4-F999-434C-B3F4-467FAFA13E2E", "name": "Dresses"},   # Bridesmaid Dresses
    {"id": "7B69E34F-43A3-4143-A22D-30786EE97998", "name": "Dresses"},   # Jumpsuits
    {"id": "7D611AF5-5135-4BBB-86F6-E80179F8E5B8", "name": "Dresses"},   # Rompers
    # ── Tops & Blouses ───────────────────────────────────────────────────────
    {"id": "5A3E7341-18B5-4C61-BFCD-8965B3479A9A", "name": "Tops & Blouses"},  # Blouses & Shirts
    {"id": "1357251872037146624",                   "name": "Tops & Blouses"},  # Ladies Short Sleeve
    {"id": "2409230541301627300",                   "name": "Tops & Blouses"},  # Women's Camis
    {"id": "2502190153271613100",                   "name": "Tops & Blouses"},  # Short-Sleeved Shirts
    {"id": "2502190153531612600",                   "name": "Tops & Blouses"},  # Long-Sleeved Shirts
    {"id": "2502140253001614100",                   "name": "Tops & Blouses"},  # Women's Vests
    # ── Knitwear ─────────────────────────────────────────────────────────────
    {"id": "DE9C662C-3F48-4855-87E7-E18733EFF6D2", "name": "Knitwear"},  # Sweaters
    # ── Co-ords & Sets ───────────────────────────────────────────────────────
    {"id": "ECDBD4C4-7467-4831-9F55-740E3C7968BE", "name": "Co-ords"},   # Suits & Sets
    # ── Outerwear ────────────────────────────────────────────────────────────
    {"id": "07398ADB-FC5E-4CC4-AD00-EB230E779E88", "name": "Outerwear"}, # Blazers
    {"id": "4CF7E664-A644-4B96-951B-B76FA973320A", "name": "Outerwear"}, # Basic Jackets
    {"id": "441DA450-5E5F-41DF-8911-3BAE883C30E8", "name": "Outerwear"}, # Trench Coats
    {"id": "D680731F-1AE8-46E4-9BE7-E98C39F07E1E", "name": "Outerwear"}, # Leather & Suede
    {"id": "1366AF62-E9CB-4834-9EC9-6126C077B5E0", "name": "Outerwear"}, # Wool & Blend
    {"id": "2409230541081607100",                   "name": "Outerwear"}, # Padded Jackets
    # ── Loungewear ───────────────────────────────────────────────────────────
    {"id": "5E656DFB-9BAE-44DD-A755-40AFA2E0E686", "name": "Loungewear"}, # Hoodies & Sweatshirts
    # ── Bottoms ──────────────────────────────────────────────────────────────
    {"id": "3B8946E7-B608-4DAB-B2F0-C425B7875035", "name": "Bottoms"},   # Skirts
    {"id": "9694B484-7EA0-4D71-993B-9CF02D24B271", "name": "Bottoms"},   # Pants & Capris
    {"id": "A7DE167B-ECFF-481E-A52A-2E7937BFAA95", "name": "Bottoms"},   # Wide Leg Pants
    {"id": "396E962A-5632-49C2-B9BF-9529DE3B9141", "name": "Bottoms"},   # Leggings
    {"id": "8A22518D-0C6F-430D-8CD9-7E043062A279", "name": "Bottoms"},   # Shorts
    # ── Denim ────────────────────────────────────────────────────────────────
    {"id": "63584B9B-5275-4268-8BEA-7D3C7A7BB925", "name": "Denim"},     # Woman Jeans
    # ── Heels ────────────────────────────────────────────────────────────────
    {"id": "638284D0-3651-4FC9-9F25-B0A0BA323D83", "name": "Heels"},     # Pumps
    # ── Flats ────────────────────────────────────────────────────────────────
    {"id": "F35FC838-1CFE-49D1-A8CA-CF7401F9C444", "name": "Flats"},     # Flats
    # ── Boots ────────────────────────────────────────────────────────────────
    {"id": "1988B912-7A18-4ED2-B1E1-61ED290A0E82", "name": "Boots"},     # Woman Boots
    # ── Sneakers ─────────────────────────────────────────────────────────────
    {"id": "1B559D30-B370-4C8E-8CFD-1E1BC47E217F", "name": "Sneakers"},  # Vulcanize Shoes
    # ── Sandals ──────────────────────────────────────────────────────────────
    {"id": "AAB54987-4E92-40C7-B0F5-5E814C1E6980", "name": "Sandals"},   # Woman Sandals
    # ── Mules ────────────────────────────────────────────────────────────────
    {"id": "8F756420-4840-474E-B2D6-6725ED219970", "name": "Mules"},     # Woman Slippers
    # ── Tote Bags ────────────────────────────────────────────────────────────
    {"id": "8F3ADC01-68FE-4CBE-BB1D-0DE42A730749", "name": "Tote Bags"}, # Totes
    # ── Crossbody Bags ───────────────────────────────────────────────────────
    {"id": "2410301013451614000",                   "name": "Crossbody Bags"}, # Women's Crossbody
    # ── Clutches ─────────────────────────────────────────────────────────────
    {"id": "CB7C7348-41DC-4AA5-9BD0-CC2D555899BB", "name": "Clutches"},  # Clutches
    {"id": "33AFFE07-CC46-4557-9FD9-27CC9975BEED", "name": "Clutches"},  # Evening Bags
    # ── Shoulder Bags ────────────────────────────────────────────────────────
    {"id": "7DC7FA45-C8E1-4A2E-BA84-B81FB9CA2815", "name": "Shoulder Bags"}, # Shoulder Bags
    {"id": "78BCE010-8E22-416F-82E2-6E5C6AE0CECE", "name": "Shoulder Bags"}, # Fashion Backpacks
    # ── Jewellery ────────────────────────────────────────────────────────────
    {"id": "95D9F317-1DB3-4E42-A031-02223215B9C5", "name": "Jewellery"}, # Necklaces & Pendants
    {"id": "D28405AE-66C6-42E6-BFF0-D6FDCB5C083C", "name": "Jewellery"}, # Earrings
    {"id": "0615F8DB-C10F-4BEF-892B-1C5B04268938", "name": "Jewellery"}, # Bracelets & Bangles
    {"id": "56B4F8B6-8600-4A18-913E-53F2F693EC2C", "name": "Jewellery"}, # Rings
    {"id": "552F095A-904C-40E4-A43B-0CD1CE15D29F", "name": "Jewellery"}, # 925 Silver Jewelry
    {"id": "84ED4B7F-D7C3-412F-AF18-04F25C91985C", "name": "Jewellery"}, # Pearls Jewelry
    {"id": "D7CE9827-F50A-4B07-84BF-1BFE44188A1C", "name": "Jewellery"}, # Fine Earrings
    {"id": "FCE034F6-A2BF-47E3-852F-FA9F67F904B2", "name": "Jewellery"}, # Engagement Rings
    {"id": "04B879BE-79E7-4CB9-B493-B03F628B5130", "name": "Jewellery"}, # Bridal Jewelry Sets
    {"id": "A044AC0D-BA3B-4967-8300-1BD57F00048E", "name": "Jewellery"}, # Women's Dress Watches
    {"id": "F40CB152-1391-4CA9-9BAE-0316DA2D3D2B", "name": "Jewellery"}, # Women's Bracelet Watches
    # ── Scarves & Accessories ────────────────────────────────────────────────
    {"id": "0DC4DF6F-4EC5-47DF-B20D-863ADF69319F", "name": "Scarves"},   # Scarves & Wraps
    {"id": "1E4A1FD7-738C-4AEF-9793-BDE062158BD6", "name": "Accessories"}, # Belts
    {"id": "F72DD534-E394-4958-B591-149C488648D7", "name": "Accessories"}, # Woman Hats & Caps
    # ── Skincare ─────────────────────────────────────────────────────────────
    {"id": "EDE3FAD9-0E6C-4F7C-9016-A2299469AA7C", "name": "Skincare"},  # Facial Care
    {"id": "B6A8B971-793B-4F9E-AA56-3A5D12F63827", "name": "Skincare"},  # Sun Care
    {"id": "E0238E88-0C63-427F-812E-BA1FCE4C67B4", "name": "Skincare"},  # Body Care
    {"id": "88AF62DE-5586-40E4-A287-864523D9AE50", "name": "Skincare"},  # Face Masks
    # ── Makeup ───────────────────────────────────────────────────────────────
    {"id": "B68DF53F-4DD5-4659-A530-66D414CF2147", "name": "Makeup"},    # Lipstick
    {"id": "8FB2C16C-4C1B-4B5A-89F8-BC30FB2C442A", "name": "Makeup"},    # Eyeshadow
    {"id": "426792A7-4906-403D-AD17-8293AFF00E66", "name": "Makeup"},    # Makeup Sets
    {"id": "A30E8F55-DC2C-4842-9372-91B96DEFDCC2", "name": "Makeup"},    # Makeup Brushes
    {"id": "E31E5996-7B86-4FEC-B929-9AEB11E76853", "name": "Makeup"},    # False Eyelashes
    {"id": "2502140902411611700",                   "name": "Makeup"},    # Eyebrow Pencil
    # ── Hair ─────────────────────────────────────────────────────────────────
    {"id": "2502140903111619100",                   "name": "Hair"},      # Hair Accessories
    {"id": "44733589-BEE4-448D-86F9-A1B5A9710C79", "name": "Hair"},      # Human Hair Wigs
    {"id": "DB81767B-2083-4C66-8E8D-1A0D897ABA7C", "name": "Hair"},      # Synthetic Wigs
    {"id": "6ADDD8E4-4141-4B5A-9A85-6D87FED7799C", "name": "Hair"},      # Synthetic Hair Pieces
    {"id": "B30591BD-0353-4791-8BF6-F4876CC7F9B1", "name": "Hair"},      # Hair Braids
]

# Keep for fix-categories endpoint compatibility
WOMENS_CATEGORY_IDS = WOMENS_LEAF_CATEGORIES


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


@router.post("/fix-categories")
def fix_product_categories(
    commerce_store_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Update short_description on all existing CJ products to use the correct
    second-level category label based on SKU prefix matching via reimport mapping.
    Matches products by slug prefix to each category's imported SKU range.
    Uses the WOMENS_CATEGORY_IDS list to bulk-update short_description.
    """
    updated = 0
    for cat in WOMENS_CATEGORY_IDS:
        # Find products whose short_description is a leaf-level CJ name
        # (not matching our second-level label) and reassign them.
        # We identify them by checking which SKUs were imported per page.
        # Simpler: update any product whose short_description is NOT already
        # one of our known category labels — bulk-assign by querying CJ API
        # to match SKUs. Instead, do a simpler fix: for each known label,
        # only update products that have short_description values that are
        # sub-names of that category (leaf names contain the parent's theme).
        pass

    # Practical fix: for each category, find products with short_description
    # NOT in our label list and try to remap by known leaf→label mapping.
    LEAF_TO_LABEL = {
        # Nail Art & Tools leaves
        "Nail Art Kits": "Nail Art & Tools",
        "Nail Gel": "Nail Art & Tools",
        "Nail Glitters": "Nail Art & Tools",
        "Stickers & Decals": "Nail Art & Tools",
        "Nail Decorations": "Nail Art & Tools",
        "Nail Dryers": "Nail Art & Tools",
        "Nail Files & Buffers": "Nail Art & Tools",
        "Nail Tips": "Nail Art & Tools",
        # Tops & Sets
        "T-Shirts": "Tops & Sets",
        "Blouses & Shirts": "Tops & Sets",
        "Tank Tops & Camis": "Tops & Sets",
        "Bodysuits": "Tops & Sets",
        "Sets": "Tops & Sets",
        "Suits & Blazers": "Tops & Sets",
        "Jumpsuits & Rompers": "Tops & Sets",
        "Hoodies & Sweatshirts": "Tops & Sets",
        # Bottoms
        "Pants & Leggings": "Bottoms",
        "Jeans": "Bottoms",
        "Skirts": "Bottoms",
        "Shorts": "Bottoms",
        "Dresses": "Bottoms",
        # Outerwear & Jackets
        "Jackets": "Outerwear & Jackets",
        "Coats": "Outerwear & Jackets",
        "Vests": "Outerwear & Jackets",
        "Trench Coats": "Outerwear & Jackets",
        # Weddings & Events
        "Wedding Dresses": "Weddings & Events",
        "Evening Dresses": "Weddings & Events",
        "Bridesmaid Dresses": "Weddings & Events",
        "Cocktail Dresses": "Weddings & Events",
        # Accessories
        "Scarves & Wraps": "Accessories",
        "Belts & Cummerbunds": "Accessories",
        "Woman Hats & Caps": "Accessories",
        "Woman Socks": "Accessories",
        "Woman Gloves & Mittens": "Accessories",
        "Eyewear & Accessories": "Accessories",
        # Women's Shoes
        "Pumps & Heels": "Women's Shoes",
        "Flats": "Women's Shoes",
        "Boots": "Women's Shoes",
        "Sandals": "Women's Shoes",
        "Sneakers": "Women's Shoes",
        "Slippers": "Women's Shoes",
        "Wedges": "Women's Shoes",
        # Women's Luggage & Bags
        "Shoulder Bags": "Women's Luggage & Bags",
        "Tote Bags": "Women's Luggage & Bags",
        "Clutches": "Women's Luggage & Bags",
        "Crossbody Bags": "Women's Luggage & Bags",
        "Backpacks": "Women's Luggage & Bags",
        "Wallets": "Women's Luggage & Bags",
        # Fashion Jewelry
        "Necklaces": "Fashion Jewelry",
        "Earrings": "Fashion Jewelry",
        "Bracelets": "Fashion Jewelry",
        "Rings": "Fashion Jewelry",
        "Anklets": "Fashion Jewelry",
        "Brooches": "Fashion Jewelry",
        # Fine Jewelry
        "Gold Jewelry": "Fine Jewelry",
        "Silver Jewelry": "Fine Jewelry",
        "Diamond Jewelry": "Fine Jewelry",
        # Wedding & Engagement
        "Engagement Rings": "Wedding & Engagement",
        "Wedding Bands": "Wedding & Engagement",
        "Wedding Jewelry Sets": "Wedding & Engagement",
        # Women's Watches
        "Quartz Watches": "Women's Watches",
        "Fashion Watches": "Women's Watches",
        "Smart Watches": "Women's Watches",
        # Skin Care
        "Face Care": "Skin Care",
        "Body Care": "Skin Care",
        "Sun Care": "Skin Care",
        "Eye Care": "Skin Care",
        "Lip Care": "Skin Care",
        "Facial Masks": "Skin Care",
        # Makeup
        "Face Makeup": "Makeup",
        "Eye Makeup": "Makeup",
        "Lip Makeup": "Makeup",
        "Nail Makeup": "Makeup",
        "Makeup Tools": "Makeup",
        # Beauty Tools
        "Facial Care Tools": "Beauty Tools",
        "Hair Removal": "Beauty Tools",
        "Massagers": "Beauty Tools",
        # Hair & Accessories
        "Hair Accessories": "Hair & Accessories",
        "Hair Extensions": "Hair & Accessories",
        "Hair Care": "Hair & Accessories",
        # Wigs & Extensions
        "Lace Wigs": "Wigs & Extensions",
        "Headband Wigs": "Wigs & Extensions",
        "Clip In Extensions": "Wigs & Extensions",
    }

    known_labels = {cat["name"] for cat in WOMENS_CATEGORY_IDS}
    products = db.query(Product).filter(
        Product.commerce_store_id == commerce_store_id,
        Product.source == "cj",
    ).all()

    for p in products:
        if p.short_description in known_labels:
            continue  # already correct
        new_label = LEAF_TO_LABEL.get(p.short_description)
        if new_label:
            p.short_description = new_label
            updated += 1

    db.commit()
    return {"updated": updated, "total_checked": len(products)}


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


# Keywords that definitively identify non-fashion / wrong-category products.
# If a product name contains any of these we skip it at import time.
_NON_FASHION_KEYWORDS = {
    # Kitchen / Cookware / Teaware
    "air fryer", "fryer", "oven", "microwave", "blender", "toaster",
    "coffee maker", "rice cooker", "slow cooker", "pressure cooker", "food processor",
    "mixer", "juicer", "dishwasher", "refrigerator", "washing machine",
    "teapot", "tea pot", "tea set", "kettle", "coffee pot", "coffee cup",
    "mug set", "cup set", "saucepan", "frying pan", "wok ", "cookware",
    "casserole", "baking tray", "baking mold", "cake mold", "pot set",
    "utensil", "spatula", "colander", "chopping board", "knife set",
    "water bottle", "thermos", "flask", "lunch box", "chopstick",
    # Electronics
    "laptop", "computer", "tablet", "phone case", "charger", "cable", "earphone",
    "earbuds", "headphone", "speaker", "bluetooth", "wifi", "router", "keyboard",
    "mouse pad", "webcam", "projector", "drone", "camera lens", "power bank",
    "led light", "night light", "table lamp", "smart watch band",
    # Tools / Hardware
    "drill", "screwdriver", "wrench", "hammer", "saw", "toolbox", "ladder",
    # Pets / Garden / Automotive
    "dog collar", "dog lead", "dog harness", "cat food", "pet collar", "bird cage",
    "plant pot", "garden hose", "car seat", "steering wheel", "car cover",
    # Health / Medical (non-beauty)
    "blood pressure", "glucose meter", "thermometer", "pulse oximeter",
    "nebulizer", "cpap", "wheelchair", "crutch", "hearing aid",
    # Toys / Baby (non-fashion)
    "lego", "toy car", "board game", "puzzle", "doll house", "baby formula",
    "baby bottle", "breast pump", "stroller",
    # Food / Supplements
    "protein powder", "vitamin supplement", "collagen powder", "energy drink",
    "snack", "chocolate bar", "coffee bean", "tea bag",
    # Office / Stationery
    "sticky note", "stapler", "ink cartridge",
    # Men's items (not "women's" — those are fine)
    "men's suit", "men's shirt", "men's trouser", "men's jacket",
    "men's hoodie", "men's jeans", "men's short", "men's coat",
    "men's sneaker", "men's shoe", "men's boot", "men's wallet",
    "men's watch", "men's underwear", "men's sock",
    "for men", "for him", "his and hers",
    # Silver serving ware / decorative objects (appear in CJ's 925 Silver category)
    "serving pot", "beverage dispenser", "tea cup", "tea vessel", "teacup",
    "tea caddy", "tea tray", "silver bowl", "silver vase", "silver jar",
    "silver platter", "silver pitcher", "silver plate", "serving bowl",
    "decorative vase", "decorative bowl", "ornate bowl", "enamel cup",
    "gourd vase", "ceramic mug", "sugar bowl", "creamer set",
    "incense burner", "candle holder", "figurine", "statue", "ornament",
    "wind chime", "silver spoon", "chopstick", "chopsticks",
    # Tech wearables (non-fashion)
    "smartwatch", "smart watch", "fitness tracker", "activity tracker",
    "heart rate monitor", "step counter", "gps watch",
}

# Explicit men's labels in the product name.
# We check AFTER confirming no women/female/ladies keyword is present.
_MENS_SIGNALS = [
    "men's", "mens ", " for men", " men ",
    "male ", "male fashion", "male clothing",
    "boy's ", "boys ", "boys'",
    "gentleman", "masculine",
    # Men's-specific clothing items (rarely/never used in women's fashion names on CJ)
    "swim trunks", "swim trunk", "board shorts", "board short",
    "cargo shorts", "cargo pant", "cargo trouser",
    "polo shirt", "polo tee",
    "boxer short", "boxer brief", "jockstrap",
    "vest and shorts", "vest and ankle", "vest and trouser", "vest and pant",
    "shirt and shorts", "shirt and trouser", "shirt and pant",
    "sleeveless vest and", "hoodie and short",
    "ankle-cuff short", "ankle cuff short",
    "linen vest short", "linen short set", "linen shirt set",
    "hawaiian shirt", "hawaiian print shirt",
    "muscle tee", "muscle shirt", "gym vest",
    "henley shirt", "henley tee",
    "button down shirt set", "beach shirt set",
    # Men's shoe types not in women's
    "oxford shoe", "derby shoe", "monk strap",
    "loafer for men", "dress shoe for men",
]

# Broad SQL ILIKE patterns for catching men's items in the DB.
# Used by purge-wrong-items endpoint.
MENS_SQL_PATTERNS = [
    "%men's%", "%mens %", "% for men%", "% men %",
    "%male %", "%male fashion%",
    "%gentleman%", "%masculine%",
    "%swim trunks%", "%board shorts%", "%board short%",
    "%cargo shorts%", "%cargo pant%", "%cargo trouser%",
    "%polo shirt%", "%polo tee%",
    "%boxer short%", "%boxer brief%",
    "%vest and shorts%", "%vest and ankle%", "%vest and trouser%", "%vest and pant%",
    "%shirt and shorts%", "%shirt and trouser%",
    "%sleeveless vest and%",
    "%ankle-cuff short%", "%ankle cuff short%",
    "%linen vest short%", "%linen short set%",
    "%hawaiian shirt%",
    "%muscle tee%", "%muscle shirt%", "%gym vest%",
    "%henley shirt%", "%henley tee%",
]

def _is_non_fashion(name: str) -> bool:
    """Return True if the product name contains a non-fashion keyword."""
    lower = name.lower()
    return any(kw in lower for kw in _NON_FASHION_KEYWORDS)

def _is_mens_product(name: str) -> bool:
    """Return True if the product is clearly men's-only (and not unisex women's)."""
    lower = name.lower()
    # If it explicitly mentions women/female it stays
    if any(w in lower for w in ("women", "woman", "female", "ladies", "lady", "girls", "girl")):
        return False
    return any(sig in lower for sig in _MENS_SIGNALS)


@router.post("/clean-inventory")
def clean_inventory(
    commerce_store_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Purge men's products and non-fashion items from existing inventory.
    Safe to run repeatedly — only deletes products that fail the fashion filter.
    """
    from app.models.product import ProductImage
    products = db.query(Product).filter(
        Product.commerce_store_id == commerce_store_id,
        Product.source == "cj",
    ).all()

    deleted = 0
    for p in products:
        if _is_mens_product(p.name) or _is_non_fashion(p.name):
            db.delete(p)
            deleted += 1

    db.commit()
    return {"deleted": deleted, "checked": len(products)}


@router.delete("/purge-wrong-items")
def purge_wrong_items(
    commerce_store_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Hard-delete non-fashion / men's / serving-ware items using SQL ILIKE patterns.
    Catches items that slipped through the Python blocklist (e.g. before it was expanded).
    Safe to run repeatedly.
    """
    from sqlalchemy import or_

    # SQL ILIKE patterns — each catches a class of wrong products
    bad_patterns = [
        # Silver serving ware
        "%serving pot%", "%beverage dispenser%", "%tea cup%", "%tea vessel%",
        "%tea caddy%", "%tea tray%", "%silver bowl%", "%silver vase%",
        "%silver jar%", "%silver platter%", "%silver pitcher%", "%serving bowl%",
        "%decorative vase%", "%ornate bowl%", "%enamel cup%", "%gourd vase%",
        "%ceramic mug%", "%sugar bowl%", "%enamel bowl%", "%silver pot%",
        "%incense burner%", "%candle holder%", "%figurine%", "%wind chime%",
        "%teapot%", "%tea pot%", "%tea set%",
        "%platter%", "%serving dish%", "%trinket box%",
        "%ornamental%", "%decorative plate%", "%enamel box%",
        # Kitchen
        "%air fryer%", "%frying pan%", "%rice cooker%", "%slow cooker%",
        "%pressure cooker%", "%food processor%", "%cookware%", "%saucepan%",
        # Tech wearables
        "%smartwatch%", "%smart watch%", "%fitness tracker%", "%activity tracker%",
        # Men's — explicit labels
        "%men's suit%", "%men's shirt%", "%men's trouser%", "%men's jacket%",
        "%men's hoodie%", "%men's jeans%", "%men's sneaker%", "%men's shoe%",
        "%men's short%", "%men's vest%", "%men's top%", "%men's coat%",
        "% for men%", "%male fashion%", "%male clothing%", "%gentleman%",
        # Men's — clothing patterns (generic names, no "men's" label)
        "%swim trunks%", "%board shorts%", "%board short%",
        "%cargo shorts%", "%cargo pant%",
        "%polo shirt%", "%polo tee%",
        "%boxer short%", "%boxer brief%",
        "%vest and shorts%", "%vest and ankle%", "%vest and pant%",
        "%shirt and shorts%", "%sleeveless vest and%",
        "%ankle-cuff short%", "%ankle cuff short%",
        "%linen vest short%", "%linen short set%",
        "%hawaiian shirt%", "%muscle tee%", "%muscle shirt%",
        "%henley shirt%", "%henley tee%",
    ]

    filters = or_(*[Product.name.ilike(p) for p in bad_patterns])
    candidates = db.query(Product).filter(
        Product.commerce_store_id == commerce_store_id,
        Product.source == "cj",
        filters,
    ).all()

    deleted = 0
    # Items matching these are always deleted even if "women" appears (e.g. "Men Women" smartwatch)
    FORCE_DELETE_SIGNALS = (
        "smartwatch", "smart watch", "fitness tracker", "heart rate", "activity tracker",
        "platter", "serving dish", "teapot", "tea pot",
        "swim trunks", "board shorts", "cargo shorts", "cargo pant",
        "polo shirt", "polo tee", "boxer short", "boxer brief",
        "vest and shorts", "vest and ankle", "sleeveless vest and",
        "ankle-cuff short", "ankle cuff short", "hawaiian shirt",
        "muscle tee", "muscle shirt", "henley shirt",
    )
    for p in candidates:
        lower = (p.name or "").lower()
        is_force_delete = any(t in lower for t in FORCE_DELETE_SIGNALS)
        # Keep genuine women's items unless they're in the force-delete list
        if not is_force_delete and any(w in lower for w in ("women", "woman", "female", "ladies")):
            continue
        db.delete(p)
        deleted += 1

    db.commit()
    return {"deleted": deleted, "checked": len(candidates)}


@router.delete("/delete-products")
def delete_products_by_ids(
    ids: str = Query(..., description="Comma-separated product IDs to delete"),
    db: Session = Depends(get_db),
):
    """Delete specific products by ID — use for manual cleanup of individual items."""
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
    deleted = 0
    for pid in id_list:
        p = db.query(Product).filter(Product.id == pid).first()
        if p:
            db.delete(p)
            deleted += 1
    db.commit()
    return {"deleted": deleted, "requested": len(id_list)}


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
            if _is_non_fashion(name) or _is_mens_product(name):
                skipped += 1
                continue
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

            # Always use our category label (second-level) as short_description
            # so frontend category filters can match reliably
            short_desc = category_label or p.get("categoryName") or None
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
    Import 50 products per leaf CJ category using exact leaf IDs.
    Products are tagged with their correct Covora category name.
    ~67 leaf categories × 50 = ~3,350 correctly categorised products.
    """
    imported_count = 0
    skipped_count = 0
    failed_count = 0
    all_errors: list = []
    fatal_error = None
    category_results = []

    try:
        token = _get_access_token()

        for cat in WOMENS_LEAF_CATEGORIES:
            cat_imported = 0
            cat_skipped = 0
            cat_failed = 0

            # 50 products per leaf category, highest price first
            for page in range(1, 2):
                try:
                    imp, skip, fail, errs = _import_page_by_category_id(
                        token=token,
                        commerce_store_id=commerce_store_id,
                        db=db,
                        category_id=cat["id"],
                        category_label=cat["name"],
                        page_num=page,
                        page_size=50,
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

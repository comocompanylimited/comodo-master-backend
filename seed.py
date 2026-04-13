from decimal import Decimal
from app.db.session import SessionLocal
from app.db import base  # noqa: F401
from app.crud.user import crud_user
from app.schemas.user import UserCreate
from app.models.business import Business
from app.models.commerce_store import CommerceStore
from app.models.website import Website
from app.models.mobile_app import MobileApp
from app.models.category import Category
from app.models.brand import Brand
from app.models.product import Product, ProductImage


def seed():
    db = SessionLocal()
    try:
        if db.query(Business).first():
            print("Database already seeded. Skipping.")
            return

        admin = crud_user.get_by_email(db, email="admin@covora.com")
        if not admin:
            admin = crud_user.create(db, obj_in=UserCreate(
                email="admin@covora.com",
                password="Admin1234!",
                full_name="Covora Admin",
                role="super_admin",
                is_active=True,
            ))
            print(f"Created admin user: {admin.email}")

        business = Business(
            name="Covora",
            subtitle="Luxury Women's Fashion",
            business_type="ecommerce",
            status="active",
            region="UK",
            owner_name="Covora Owner",
        )
        db.add(business)
        db.flush()

        store = CommerceStore(
            business_id=business.id,
            name="Covora Main Store",
            status="active",
        )
        db.add(store)
        db.flush()

        website = Website(
            business_id=business.id,
            name="Covora Website",
            website_type="ecommerce",
            domain="covora.com",
            environment="production",
            status="active",
            commerce_store_id=store.id,
        )
        db.add(website)

        app = MobileApp(
            business_id=business.id,
            name="Covora App",
            app_type="shopping",
            platform="ios_android",
            version="1.0.0",
            status="active",
            commerce_store_id=store.id,
        )
        db.add(app)
        db.flush()

        categories_data = [
            ("Dresses", "dresses"),
            ("Bags", "bags"),
            ("Shoes", "shoes"),
            ("Jewellery", "jewellery"),
            ("Accessories", "accessories"),
            ("Tops", "tops"),
        ]
        cats = {}
        for name, slug in categories_data:
            cat = Category(commerce_store_id=store.id, name=name, slug=slug, status="active")
            db.add(cat)
            db.flush()
            cats[slug] = cat

        brands_data = [
            ("Maison Élite", "maison-elite", "Parisian luxury atelier"),
            ("Arcadia", "arcadia", "Contemporary British luxury"),
            ("Velour Atelier", "velour-atelier", "Couture footwear specialists"),
            ("Éclat Beauté", "eclat-beaute", "Premium beauty and skincare"),
        ]
        brnds = {}
        for name, slug, desc in brands_data:
            brand = Brand(commerce_store_id=store.id, name=name, slug=slug, description=desc, status="active")
            db.add(brand)
            db.flush()
            brnds[slug] = brand

        products_data = [
            {
                "name": "Silk Wrap Dress",
                "slug": "silk-wrap-dress",
                "sku": "SKU-001",
                "price": Decimal("285.00"),
                "compare_at_price": Decimal("395.00"),
                "sale_price": Decimal("285.00"),
                "category": "dresses",
                "brand": "maison-elite",
                "stock_quantity": 24,
                "featured": True,
                "status": "active",
                "short_description": "Fluid silk wrap dress with deep V-neckline.",
                "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&q=80",
            },
            {
                "name": "Croc-Embossed Leather Tote",
                "slug": "croc-embossed-leather-tote",
                "sku": "SKU-002",
                "price": Decimal("845.00"),
                "compare_at_price": None,
                "sale_price": None,
                "category": "bags",
                "brand": "arcadia",
                "stock_quantity": 8,
                "featured": True,
                "status": "active",
                "short_description": "Structured tote in croc-embossed leather.",
                "image": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&q=80",
            },
            {
                "name": "Strappy Heel Sandal",
                "slug": "strappy-heel-sandal",
                "sku": "SKU-003",
                "price": Decimal("385.00"),
                "compare_at_price": None,
                "sale_price": None,
                "category": "shoes",
                "brand": "velour-atelier",
                "stock_quantity": 18,
                "featured": False,
                "status": "active",
                "short_description": "Barely-there strappy heel sandal.",
                "image": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800&q=80",
            },
            {
                "name": "Gold Vermeil Cuff Bracelet",
                "slug": "gold-vermeil-cuff-bracelet",
                "sku": "SKU-004",
                "price": Decimal("285.00"),
                "compare_at_price": None,
                "sale_price": None,
                "category": "jewellery",
                "brand": "arcadia",
                "stock_quantity": 15,
                "featured": True,
                "status": "active",
                "short_description": "18k gold vermeil open cuff bracelet.",
                "image": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80",
            },
            {
                "name": "Classic Cashmere Blazer",
                "slug": "classic-cashmere-blazer",
                "sku": "SKU-005",
                "price": Decimal("595.00"),
                "compare_at_price": Decimal("795.00"),
                "sale_price": Decimal("595.00"),
                "category": "tops",
                "brand": "maison-elite",
                "stock_quantity": 10,
                "featured": True,
                "status": "active",
                "short_description": "Tailored cashmere blazer in classic black.",
                "image": "https://images.unsplash.com/photo-1549062573-edc78a53ffa0?w=800&q=80",
            },
        ]

        for pd in products_data:
            img_url = pd.pop("image")
            cat_slug = pd.pop("category")
            brand_slug = pd.pop("brand")
            product = Product(
                commerce_store_id=store.id,
                category_id=cats[cat_slug].id,
                brand_id=brnds[brand_slug].id,
                **pd,
            )
            db.add(product)
            db.flush()
            db.add(ProductImage(product_id=product.id, image_url=img_url, sort_order=0))

        db.commit()
        print("Seed completed successfully.")
        print(f"  Business: {business.name} (id={business.id})")
        print(f"  Commerce Store: {store.name} (id={store.id})")
        print(f"  Categories: {len(categories_data)}")
        print(f"  Brands: {len(brands_data)}")
        print(f"  Products: {len(products_data)}")
        print(f"  Admin login: admin@covora.com / Admin1234!")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

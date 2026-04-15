"""create all tables

Revision ID: 0000
Revises:
Create Date: 2026-04-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        full_name VARCHAR(255),
        role VARCHAR(50) NOT NULL DEFAULT 'staff',
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        subtitle VARCHAR(500),
        business_type VARCHAR(100),
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        region VARCHAR(100),
        owner_name VARCHAR(255),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_businesses_name ON businesses (name)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS commerce_stores (
        id SERIAL PRIMARY KEY,
        business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_commerce_stores_business_id ON commerce_stores (business_id)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS websites (
        id SERIAL PRIMARY KEY,
        business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        website_type VARCHAR(100),
        domain VARCHAR(255),
        environment VARCHAR(50) DEFAULT 'production',
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        commerce_store_id INTEGER REFERENCES commerce_stores(id) ON DELETE SET NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS mobile_apps (
        id SERIAL PRIMARY KEY,
        business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        app_type VARCHAR(100),
        platform VARCHAR(50),
        version VARCHAR(50),
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        commerce_store_id INTEGER REFERENCES commerce_stores(id) ON DELETE SET NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        commerce_store_id INTEGER NOT NULL REFERENCES commerce_stores(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        slug VARCHAR(255) NOT NULL,
        description TEXT,
        parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_categories_commerce_store_id ON categories (commerce_store_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_categories_slug ON categories (slug)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS brands (
        id SERIAL PRIMARY KEY,
        commerce_store_id INTEGER NOT NULL REFERENCES commerce_stores(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        slug VARCHAR(255) NOT NULL,
        description TEXT,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_brands_commerce_store_id ON brands (commerce_store_id)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        commerce_store_id INTEGER NOT NULL REFERENCES commerce_stores(id) ON DELETE CASCADE,
        name VARCHAR(500) NOT NULL,
        slug VARCHAR(500) NOT NULL,
        short_description VARCHAR(1000),
        description TEXT,
        sku VARCHAR(255) UNIQUE NOT NULL,
        barcode VARCHAR(255),
        brand_id INTEGER REFERENCES brands(id) ON DELETE SET NULL,
        category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
        price NUMERIC(12,2) NOT NULL DEFAULT 0,
        sale_price NUMERIC(12,2),
        compare_at_price NUMERIC(12,2),
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        low_stock_threshold INTEGER,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        visibility VARCHAR(50) NOT NULL DEFAULT 'visible',
        featured BOOLEAN NOT NULL DEFAULT FALSE,
        weight NUMERIC(10,4),
        source VARCHAR(50),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_commerce_store_id ON products (commerce_store_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_name ON products (name)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_slug ON products (slug)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_sku ON products (sku)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_status ON products (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_featured ON products (featured)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_source ON products (source)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS product_images (
        id SERIAL PRIMARY KEY,
        product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
        image_url VARCHAR(1000) NOT NULL,
        alt_text VARCHAR(500),
        sort_order INTEGER NOT NULL DEFAULT 0
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_images_product_id ON product_images (product_id)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS product_variants (
        id SERIAL PRIMARY KEY,
        product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        sku VARCHAR(255) UNIQUE,
        barcode VARCHAR(255),
        price NUMERIC(12,2),
        sale_price NUMERIC(12,2),
        compare_at_price NUMERIC(12,2),
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id SERIAL PRIMARY KEY,
        commerce_store_id INTEGER NOT NULL REFERENCES commerce_stores(id) ON DELETE CASCADE,
        first_name VARCHAR(255) NOT NULL,
        last_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone VARCHAR(50),
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_customers_commerce_store_id ON customers (commerce_store_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_customers_email ON customers (email)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS customer_addresses (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
        type VARCHAR(50) NOT NULL DEFAULT 'shipping',
        line1 VARCHAR(500) NOT NULL,
        line2 VARCHAR(500),
        city VARCHAR(255) NOT NULL,
        state VARCHAR(255),
        postal_code VARCHAR(50),
        country VARCHAR(100) NOT NULL,
        is_default BOOLEAN NOT NULL DEFAULT FALSE
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        commerce_store_id INTEGER NOT NULL REFERENCES commerce_stores(id) ON DELETE CASCADE,
        customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
        order_number VARCHAR(100) UNIQUE NOT NULL,
        channel VARCHAR(100) NOT NULL DEFAULT 'web',
        order_status VARCHAR(50) NOT NULL DEFAULT 'pending',
        payment_status VARCHAR(50) NOT NULL DEFAULT 'pending',
        fulfillment_status VARCHAR(50) NOT NULL DEFAULT 'unfulfilled',
        subtotal NUMERIC(12,2) NOT NULL DEFAULT 0,
        discount_total NUMERIC(12,2) NOT NULL DEFAULT 0,
        shipping_total NUMERIC(12,2) NOT NULL DEFAULT 0,
        tax_total NUMERIC(12,2) NOT NULL DEFAULT 0,
        total NUMERIC(12,2) NOT NULL DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_commerce_store_id ON orders (commerce_store_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_order_number ON orders (order_number)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
        product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
        variant_id INTEGER REFERENCES product_variants(id) ON DELETE SET NULL,
        product_name VARCHAR(500) NOT NULL,
        sku VARCHAR(255),
        quantity INTEGER NOT NULL DEFAULT 1,
        unit_price NUMERIC(12,2) NOT NULL,
        line_total NUMERIC(12,2) NOT NULL
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS discounts (
        id SERIAL PRIMARY KEY,
        commerce_store_id INTEGER NOT NULL REFERENCES commerce_stores(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        code VARCHAR(100),
        discount_type VARCHAR(50) NOT NULL,
        value NUMERIC(12,2) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        starts_at TIMESTAMPTZ,
        ends_at TIMESTAMPTZ,
        usage_limit INTEGER,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS import_jobs (
        id SERIAL PRIMARY KEY,
        commerce_store_id INTEGER NOT NULL REFERENCES commerce_stores(id) ON DELETE CASCADE,
        file_name VARCHAR(500) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        total_rows INTEGER NOT NULL DEFAULT 0,
        created_count INTEGER NOT NULL DEFAULT 0,
        updated_count INTEGER NOT NULL DEFAULT 0,
        skipped_count INTEGER NOT NULL DEFAULT 0,
        failed_count INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """)


def downgrade() -> None:
    for table in [
        "import_jobs", "discounts", "order_items", "orders",
        "customer_addresses", "customers", "product_variants",
        "product_images", "products", "brands", "categories",
        "mobile_apps", "websites", "commerce_stores", "businesses", "users",
    ]:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")

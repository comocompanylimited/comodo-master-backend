"""add stripe and customer fields to orders

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-16
"""
from alembic import op
from sqlalchemy import inspect

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing = [c["name"] for c in inspector.get_columns("orders")]

    cols = {
        "customer_name":           "ALTER TABLE orders ADD COLUMN customer_name VARCHAR(255)",
        "customer_email":          "ALTER TABLE orders ADD COLUMN customer_email VARCHAR(255)",
        "customer_phone":          "ALTER TABLE orders ADD COLUMN customer_phone VARCHAR(50)",
        "shipping_address":        "ALTER TABLE orders ADD COLUMN shipping_address VARCHAR(500)",
        "shipping_address2":       "ALTER TABLE orders ADD COLUMN shipping_address2 VARCHAR(500)",
        "shipping_city":           "ALTER TABLE orders ADD COLUMN shipping_city VARCHAR(255)",
        "shipping_postcode":       "ALTER TABLE orders ADD COLUMN shipping_postcode VARCHAR(50)",
        "shipping_country":        "ALTER TABLE orders ADD COLUMN shipping_country VARCHAR(100)",
        "stripe_session_id":       "ALTER TABLE orders ADD COLUMN stripe_session_id VARCHAR(500) UNIQUE",
        "stripe_payment_intent_id":"ALTER TABLE orders ADD COLUMN stripe_payment_intent_id VARCHAR(500)",
    }
    for col, sql in cols.items():
        if col not in existing:
            op.execute(sql)

    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_customer_email ON orders (customer_email)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_stripe_session_id ON orders (stripe_session_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_orders_stripe_payment_intent_id ON orders (stripe_payment_intent_id)")


def downgrade() -> None:
    for col in [
        "customer_name","customer_email","customer_phone",
        "shipping_address","shipping_address2","shipping_city",
        "shipping_postcode","shipping_country",
        "stripe_session_id","stripe_payment_intent_id",
    ]:
        op.execute(f"ALTER TABLE orders DROP COLUMN IF EXISTS {col}")

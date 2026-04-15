"""add weight and source to products

Revision ID: 0001
Revises:
Create Date: 2026-04-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0001"
down_revision = "0000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tables are created by Base.metadata.create_all on startup.
    # This migration only adds columns that may be missing on older deployments.
    bind = op.get_bind()
    inspector = inspect(bind)
    if "products" not in inspector.get_table_names():
        return
    existing = [c["name"] for c in inspector.get_columns("products")]
    if "weight" not in existing:
        op.execute("ALTER TABLE products ADD COLUMN weight NUMERIC(10, 4)")
    if "source" not in existing:
        op.execute("ALTER TABLE products ADD COLUMN source VARCHAR(50)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_source ON products (source)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_products_source")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS weight")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS source")

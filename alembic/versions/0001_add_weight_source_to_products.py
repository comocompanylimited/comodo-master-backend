"""add weight and source to products

Revision ID: 0001
Revises:
Create Date: 2026-04-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE products
        ADD COLUMN IF NOT EXISTS weight NUMERIC(10, 4),
        ADD COLUMN IF NOT EXISTS source VARCHAR(50)
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_products_source ON products (source)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_products_source")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS weight")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS source")

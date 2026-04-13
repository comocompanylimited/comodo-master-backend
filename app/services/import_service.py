import io
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.import_job import ImportJob
from app.models.product import Product
from app.models.commerce_store import CommerceStore


def parse_csv(file_content: bytes) -> List[Dict[str, Any]]:
    import csv
    text = file_content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def parse_xlsx(file_content: bytes) -> List[Dict[str, Any]]:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(file_content))
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(rows[0])]
    return [dict(zip(headers, row)) for row in rows[1:]]


def process_import_job(
    db: Session,
    *,
    job: ImportJob,
    rows: List[Dict[str, Any]],
    commerce_store_id: int,
) -> ImportJob:
    job.total_rows = len(rows)
    job.status = "processing"
    db.add(job)
    db.flush()

    created = updated = skipped = failed = 0

    for row in rows:
        try:
            name = str(row.get("name") or row.get("Name") or "").strip()
            sku = str(row.get("sku") or row.get("SKU") or "").strip()
            if not name or not sku:
                skipped += 1
                continue

            existing = db.query(Product).filter(
                Product.commerce_store_id == commerce_store_id,
                Product.sku == sku,
            ).first()

            price_raw = row.get("price") or row.get("Price") or "0"
            try:
                price = float(str(price_raw).replace(",", "").strip() or "0")
            except (ValueError, TypeError):
                price = 0.0

            stock_raw = row.get("stock_quantity") or row.get("stock") or row.get("Stock") or "0"
            try:
                stock = int(str(stock_raw).strip() or "0")
            except (ValueError, TypeError):
                stock = 0

            if existing:
                existing.name = name
                existing.price = price
                existing.stock_quantity = stock
                db.add(existing)
                updated += 1
            else:
                import re
                slug_base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                slug = f"{slug_base}-{sku.lower()}"
                product = Product(
                    commerce_store_id=commerce_store_id,
                    name=name,
                    slug=slug,
                    sku=sku,
                    price=price,
                    stock_quantity=stock,
                    status="active",
                )
                db.add(product)
                created += 1
        except Exception:
            failed += 1

    job.created_count = created
    job.updated_count = updated
    job.skipped_count = skipped
    job.failed_count = failed
    job.status = "completed"
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

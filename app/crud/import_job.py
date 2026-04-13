from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.import_job import ImportJob
from app.schemas.import_job import ImportJobCreate


class CRUDImportJob(CRUDBase[ImportJob, ImportJobCreate, ImportJobCreate]):
    def get_by_store(
        self, db: Session, *, commerce_store_id: int, skip: int = 0, limit: int = 50
    ) -> List[ImportJob]:
        return db.query(ImportJob).filter(
            ImportJob.commerce_store_id == commerce_store_id
        ).order_by(ImportJob.created_at.desc()).offset(skip).limit(limit).all()


crud_import_job = CRUDImportJob(ImportJob)

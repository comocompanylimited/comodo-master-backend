from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.crud.import_job import crud_import_job
from app.models.import_job import ImportJob
from app.schemas.import_job import ImportJobRead
from app.services.import_service import parse_csv, parse_xlsx, process_import_job

router = APIRouter()


@router.get("", response_model=List[ImportJobRead])
def list_import_jobs(
    commerce_store_id: int = Query(...),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    return crud_import_job.get_by_store(db, commerce_store_id=commerce_store_id, skip=skip, limit=limit)


@router.post("/upload", response_model=ImportJobRead, status_code=201)
async def upload_import_file(
    commerce_store_id: int = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    filename = file.filename or "upload"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ("csv", "xlsx"):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")

    content = await file.read()

    job = ImportJob(
        commerce_store_id=commerce_store_id,
        file_name=filename,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        if ext == "csv":
            rows = parse_csv(content)
        else:
            rows = parse_xlsx(content)
        job = process_import_job(db, job=job, rows=rows, commerce_store_id=commerce_store_id)
    except Exception as exc:
        job.status = "failed"
        db.add(job)
        db.commit()
        db.refresh(job)

    return job


@router.get("/{job_id}", response_model=ImportJobRead)
def get_import_job(job_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    obj = crud_import_job.get(db, id=job_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Import job not found")
    return obj

"""
POST /upload-report

Accepts a JPG/PNG/PDF file (and optional age/gender), stores it on disk,
and creates a `reports` row with status="uploaded". No OCR happens here -
that's the job of /extract-report - this endpoint only has to be fast and
reliable so the UI can show upload progress immediately.
"""
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report, User
from app.schemas.report_schemas import UploadResponse
from app.utils.file_utils import save_upload, validate_upload

router = APIRouter()


@router.post("/upload-report", response_model=UploadResponse)
async def upload_report(
    file: UploadFile = File(...),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    ext = validate_upload(file)

    user_id = None
    if age is not None or gender is not None:
        user = User(age=age, gender=gender)
        db.add(user)
        db.flush()
        user_id = user.id

    try:
        stored_filename, _path = await save_upload(file, ext)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {exc}") from exc

    report = Report(
        user_id=user_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_type=ext,
        status="uploaded",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return UploadResponse(
        report_id=report.id,
        original_filename=report.original_filename,
        file_type=report.file_type,
        status=report.status,
    )

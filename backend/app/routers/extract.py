"""
POST /extract-report

Runs real OCR against the previously uploaded file, parses it into
structured rows (test name/value/unit/reference range), computes a
provisional Normal/Low/High/Unknown status for each row, and persists
everything to `extracted_results`. The frontend shows this to the user so
they can correct any misread values before /analyze-report runs the AI step.
"""
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import ExtractedResult, Report
from app.schemas.report_schemas import ExtractRequest, ExtractResponse
from app.services.analysis_service import determine_status
from app.services.ocr_service import OCRError, extract_text
from app.services.parser_service import parse_report_text

router = APIRouter()


@router.post("/extract-report", response_model=ExtractResponse)
def extract_report(payload: ExtractRequest, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == payload.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    file_path = os.path.join(settings.UPLOAD_DIR, report.stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Uploaded file is missing on disk.")

    try:
        raw_text = extract_text(file_path, report.file_type)
    except OCRError as exc:
        report.status = "failed"
        report.error_message = str(exc)
        db.commit()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        report.status = "failed"
        report.error_message = f"Unexpected OCR failure: {exc}"
        db.commit()
        raise HTTPException(status_code=500, detail=report.error_message) from exc

    parsed = parse_report_text(raw_text)

    if not parsed.rows:
        report.status = "failed"
        report.raw_text = raw_text
        report.error_message = (
            "Text was extracted but no test rows could be identified. "
            "The report layout may be unusual - try a clearer image."
        )
        db.commit()
        raise HTTPException(status_code=422, detail=report.error_message)

    # Clear any previous extraction (e.g. user re-runs extraction on the same report)
    db.query(ExtractedResult).filter(ExtractedResult.report_id == report.id).delete()

    extracted_rows = []
    for row in parsed.rows:
        status = determine_status(row.numeric_value, row.reference_range)
        er = ExtractedResult(
            report_id=report.id,
            test_name=row.test_name,
            value=row.value,
            numeric_value=row.numeric_value,
            unit=row.unit,
            reference_range=row.reference_range,
            status=status,
        )
        db.add(er)
        extracted_rows.append(er)

    report.raw_text = raw_text
    report.report_date = parsed.report_date
    report.status = "extracted"
    report.error_message = None
    db.commit()
    for er in extracted_rows:
        db.refresh(er)

    return ExtractResponse(
        report_id=report.id,
        status=report.status,
        report_date=report.report_date,
        extracted_results=extracted_rows,
        raw_text_preview=raw_text[:2000],
    )

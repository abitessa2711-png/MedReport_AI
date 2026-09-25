"""
GET /reports         -> history list (filtered by user email)
GET /reports/{id}     -> full detail for one report
POST /reports/{id}/claim -> claim guest report for logged-in user
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Report, User
from app.schemas.report_schemas import ClaimReportRequest, ReportDetailOut, ReportSummaryOut

router = APIRouter()


@router.get("/reports", response_model=list[ReportSummaryOut])
def list_reports(user_email: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Report).options(joinedload(Report.analysis))
    
    if user_email:
        email_clean = user_email.strip().lower()
        query = query.filter(Report.user_email == email_clean)
    else:
        # If no user_email provided, do not expose permanent history of registered users
        query = query.filter(Report.is_guest == True)

    reports = query.order_by(Report.created_at.desc()).all()
    
    out = []
    for r in reports:
        out.append(
            ReportSummaryOut(
                id=r.id,
                original_filename=r.original_filename,
                file_type=r.file_type,
                status=r.status,
                is_guest=r.is_guest,
                user_email=r.user_email,
                report_date=r.report_date,
                created_at=r.created_at,
                overall_summary_en=r.analysis.overall_summary_en if r.analysis else None,
            )
        )
    return out


@router.get("/reports/{report_id}", response_model=ReportDetailOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .options(joinedload(Report.extracted_results), joinedload(Report.analysis))
        .filter(Report.id == report_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


@router.post("/reports/{report_id}/claim", response_model=ReportDetailOut)
def claim_report(report_id: int, payload: ClaimReportRequest, db: Session = Depends(get_db)):
    email_clean = payload.user_email.strip().lower()
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    user = db.query(User).filter(User.email == email_clean).first()
    if user:
        report.user_id = user.id

    report.user_email = email_clean
    report.is_guest = False
    db.commit()

    return get_report(report_id, db)


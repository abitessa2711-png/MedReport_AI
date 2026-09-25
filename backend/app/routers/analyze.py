"""
POST /analyze-report

1. Applies any user corrections to the OCR'd rows (e.g. fixing a misread
   "1O.2" -> "10.2"), and recomputes each row's Normal/Low/High status.
2. Builds the structured JSON described in the spec:
     { "test_name", "value", "unit", "reference_range", "status" }
3. Sends that structured JSON (never the raw image) to the configured AI
   provider to generate the English + Tamil summaries.
4. Persists the result to `analysis_results` and marks the report "analyzed".
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisResult, ExtractedResult, Report, User
from app.schemas.report_schemas import AnalyzeRequest, AnalyzeResponse
from app.services.ai_service import AIGenerationError, generate_bilingual_summary
from app.services.analysis_service import determine_status

router = APIRouter()


@router.post("/analyze-report", response_model=AnalyzeResponse)
def analyze_report(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == payload.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    rows = db.query(ExtractedResult).filter(ExtractedResult.report_id == report.id).all()
    if not rows:
        raise HTTPException(
            status_code=422,
            detail="No extracted results found. Run /extract-report first.",
        )

    # Apply optional user corrections to OCR mistakes.
    if payload.corrections:
        rows_by_id = {r.id: r for r in rows}
        for correction in payload.corrections:
            row = rows_by_id.get(correction.id)
            if not row:
                continue
            changed = False
            if correction.test_name is not None and correction.test_name != row.test_name:
                row.test_name = correction.test_name
                changed = True
            if correction.value is not None and correction.value != row.value:
                row.value = correction.value
                try:
                    row.numeric_value = float(correction.value.replace(",", ""))
                except ValueError:
                    row.numeric_value = None
                changed = True
            if correction.unit is not None and correction.unit != row.unit:
                row.unit = correction.unit
                changed = True
            if correction.reference_range is not None and correction.reference_range != row.reference_range:
                row.reference_range = correction.reference_range
                changed = True
            if changed:
                row.was_corrected = True
                row.status = determine_status(row.numeric_value, row.reference_range)

    # Optionally record/refresh patient age & gender for this report.
    if payload.age is not None or payload.gender is not None:
        if report.user_id:
            user = db.query(User).filter(User.id == report.user_id).first()
        else:
            user = User()
            db.add(user)
            db.flush()
            report.user_id = user.id
        if payload.age is not None:
            user.age = payload.age
        if payload.gender is not None:
            user.gender = payload.gender

    db.flush()

    structured_results = [
        {
            "test_name": r.test_name,
            "value": r.value,
            "unit": r.unit,
            "reference_range": r.reference_range,
            "status": r.status,
        }
        for r in rows
    ]

    try:
        summary = generate_bilingual_summary(
            structured_results,
            age=payload.age,
            gender=payload.gender,
            report_date=report.report_date,
        )
    except AIGenerationError as exc:
        report.status = "failed"
        report.error_message = f"AI summary generation failed: {exc}"
        db.commit()
        raise HTTPException(status_code=502, detail=report.error_message) from exc

    # Replace any previous analysis for this report.
    existing = db.query(AnalysisResult).filter(AnalysisResult.report_id == report.id).first()
    if existing:
        db.delete(existing)
        db.flush()

    if payload.user_email:
        report.user_email = payload.user_email.strip().lower()
        report.is_guest = False

    analysis = AnalysisResult(
        report_id=report.id,
        overall_summary_en=summary["overall_summary_en"],
        overall_summary_ta=summary["overall_summary_ta"],
        abnormal_findings_en=summary["abnormal_findings_en"],
        abnormal_findings_ta=summary["abnormal_findings_ta"],
        normal_findings_en=summary["normal_findings_en"],
        normal_findings_ta=summary["normal_findings_ta"],
        attention_points_en=summary["attention_points_en"],
        attention_points_ta=summary["attention_points_ta"],
        lifestyle_en=summary.get("lifestyle_en"),
        lifestyle_ta=summary.get("lifestyle_ta"),
        prevention_en=summary.get("prevention_en"),
        prevention_ta=summary.get("prevention_ta"),
        ai_provider=summary["ai_provider"],
        ai_model=summary["ai_model"],
    )
    db.add(analysis)

    report.status = "analyzed"
    report.error_message = None
    db.commit()

    db.refresh(analysis)
    for r in rows:
        db.refresh(r)

    return AnalyzeResponse(
        report_id=report.id,
        status=report.status,
        extracted_results=rows,
        analysis=analysis,
    )

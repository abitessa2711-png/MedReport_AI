"""
Pydantic request/response models for the API.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class UserRegister(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClaimReportRequest(BaseModel):
    user_email: str


class ExtractedResultOut(BaseModel):
    id: int
    test_name: str
    value: Optional[str] = None
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = None
    was_corrected: bool = False

    model_config = ConfigDict(from_attributes=True)


class ExtractedResultCorrection(BaseModel):
    """Payload for correcting one OCR-extracted row before analysis."""
    id: int
    test_name: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None


class AnalysisResultOut(BaseModel):
    overall_summary_en: Optional[str] = None
    overall_summary_ta: Optional[str] = None
    abnormal_findings_en: Optional[str] = None
    abnormal_findings_ta: Optional[str] = None
    normal_findings_en: Optional[str] = None
    normal_findings_ta: Optional[str] = None
    attention_points_en: Optional[str] = None
    attention_points_ta: Optional[str] = None
    lifestyle_en: Optional[str] = None
    lifestyle_ta: Optional[str] = None
    prevention_en: Optional[str] = None
    prevention_ta: Optional[str] = None
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReportSummaryOut(BaseModel):
    """Lightweight shape used in the history list."""
    id: int
    original_filename: str
    file_type: str
    status: str
    is_guest: Optional[bool] = False
    user_email: Optional[str] = None
    report_date: Optional[str] = None
    created_at: datetime
    overall_summary_en: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReportDetailOut(BaseModel):
    id: int
    original_filename: str
    file_type: str
    status: str
    is_guest: Optional[bool] = False
    user_email: Optional[str] = None
    error_message: Optional[str] = None
    report_date: Optional[str] = None
    raw_text: Optional[str] = None
    created_at: datetime
    extracted_results: List[ExtractedResultOut] = []
    analysis: Optional[AnalysisResultOut] = None

    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    report_id: int
    original_filename: str
    file_type: str
    status: str


class ExtractRequest(BaseModel):
    report_id: int


class ExtractResponse(BaseModel):
    report_id: int
    status: str
    report_date: Optional[str] = None
    extracted_results: List[ExtractedResultOut]
    raw_text_preview: str


class AnalyzeRequest(BaseModel):
    report_id: int
    user_email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    symptoms: Optional[str] = None
    corrections: Optional[List[ExtractedResultCorrection]] = None


class AnalyzeResponse(BaseModel):
    report_id: int
    status: str
    extracted_results: List[ExtractedResultOut]
    analysis: AnalysisResultOut


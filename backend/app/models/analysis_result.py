from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)

    overall_summary_en = Column(Text, nullable=True)
    overall_summary_ta = Column(Text, nullable=True)
    abnormal_findings_en = Column(Text, nullable=True)
    abnormal_findings_ta = Column(Text, nullable=True)
    normal_findings_en = Column(Text, nullable=True)
    normal_findings_ta = Column(Text, nullable=True)
    attention_points_en = Column(Text, nullable=True)
    attention_points_ta = Column(Text, nullable=True)
    lifestyle_en = Column(Text, nullable=True)
    lifestyle_ta = Column(Text, nullable=True)
    prevention_en = Column(Text, nullable=True)
    prevention_ta = Column(Text, nullable=True)

    ai_provider = Column(String(50), nullable=True)
    ai_model = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    report = relationship("Report", back_populates="analysis")


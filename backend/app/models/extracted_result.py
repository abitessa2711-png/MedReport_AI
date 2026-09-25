from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class ExtractedResult(Base):
    __tablename__ = "extracted_results"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String(255), nullable=False)
    value = Column(String(50), nullable=True)
    numeric_value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    status = Column(String(20), nullable=True)
    was_corrected = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    report = relationship("Report", back_populates="extracted_results")

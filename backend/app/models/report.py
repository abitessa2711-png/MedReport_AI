from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_email = Column(String(255), index=True, nullable=True)
    is_guest = Column(Boolean, default=True, nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    report_date = Column(String(50), nullable=True)
    raw_text = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="uploaded")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="reports")
    extracted_results = relationship(
        "ExtractedResult", back_populates="report", cascade="all, delete-orphan"
    )
    analysis = relationship(
        "AnalysisResult", back_populates="report", uselist=False, cascade="all, delete-orphan"
    )


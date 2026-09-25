"""
FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers import analyze, auth, extract, reports, upload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medreport")

app = FastAPI(
    title="AI-Based Medical Report Image Analysis & Bilingual Summary System",
    description=(
        "Upload a lab report image/PDF, extract real test values via OCR, "
        "and generate an English + Tamil plain-language summary. "
        "Educational tool only - not a medical diagnosis."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Auth"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(extract.router, tags=["Extraction"])
app.include_router(analyze.router, tags=["Analysis"])
app.include_router(reports.router, tags=["Reports"])



@app.on_event("startup")
def on_startup():
    # Creates any tables that don't exist yet. For a fresh setup, prefer
    # running database/schema.sql directly - this is a convenience fallback.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        logger.warning(
            "Could not verify/create database tables on startup (%s). "
            "Make sure MySQL is running and .env is configured, then run "
            "database/schema.sql manually if needed.",
            exc,
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "medreport-ai-backend",
        "disclaimer": (
            "This tool summarizes information found in an uploaded report. "
            "It is not a medical diagnosis. Please consult a qualified "
            "healthcare professional for medical interpretation."
        ),
    }

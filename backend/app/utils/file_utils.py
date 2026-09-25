"""
Helpers for saving/validating uploaded files.
"""
import os
import uuid
from typing import Tuple

from fastapi import UploadFile, HTTPException

from app.config import settings

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}


def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


def validate_upload(file: UploadFile) -> str:
    ext = get_extension(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: jpg, jpeg, png, pdf.",
        )
    return ext


async def save_upload(file: UploadFile, ext: str) -> Tuple[str, str]:
    """Streams the upload to disk with a size limit, returns (stored_filename, path)."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    size = 0
    try:
        with open(path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    out_file.close()
                    os.remove(path)
                    raise HTTPException(
                        status_code=400,
                        detail=f"File exceeds the {settings.MAX_UPLOAD_MB}MB upload limit.",
                    )
                out_file.write(chunk)
    finally:
        await file.close()

    if size == 0:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=400, detail="Uploaded file is empty or corrupted.")

    return stored_filename, path

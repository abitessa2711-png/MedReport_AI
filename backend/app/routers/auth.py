"""
User authentication router.
Handles registration, login, and user profile checks.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hashlib

from app.database import get_db
from app.models import User
from app.schemas.report_schemas import UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.post("/register", response_model=UserOut)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    if len(payload.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters long.")

    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    hashed = hash_password(payload.password)
    user = User(
        email=email_clean,
        password_hash=hashed,
        full_name=payload.full_name or email_clean.split("@")[0].capitalize(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=UserOut)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    hashed = hash_password(payload.password)

    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if user.password_hash and user.password_hash != hashed:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return user


@router.get("/me", response_model=UserOut)
def get_current_user(email: str, db: Session = Depends(get_db)):
    email_clean = email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

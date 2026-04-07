"""
Authentication routes for CompareKart.
Provides basic user registration and login backed by the database.
"""

import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserAccount
from schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserProfileResponse,
    AuthResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _hash_password(password: str) -> str:
    """Hash password with random salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()
    return f"{salt}${digest}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify plaintext password against stored salt$hash format."""
    try:
        salt, expected = stored_hash.split("$", 1)
    except ValueError:
        return False

    actual = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()
    return secrets.compare_digest(actual, expected)


@router.post("/register", response_model=AuthResponse)
async def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing = db.query(UserAccount).filter(UserAccount.user_id == payload.user_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="User ID already exists")

    user = UserAccount(
        user_id=payload.user_id.strip(),
        password_hash=_hash_password(payload.password),
        full_name=payload.full_name.strip() if payload.full_name else None,
        email=payload.email.strip() if payload.email else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        success=True,
        message="Registration successful",
        user=UserProfileResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Login with user ID and password."""
    user = db.query(UserAccount).filter(UserAccount.user_id == payload.user_id).first()
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid user ID or password")

    return AuthResponse(
        success=True,
        message="Login successful",
        user=UserProfileResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            created_at=user.created_at,
        ),
    )


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Fetch user profile by user ID."""
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfileResponse(
        user_id=user.user_id,
        full_name=user.full_name,
        email=user.email,
        created_at=user.created_at,
    )

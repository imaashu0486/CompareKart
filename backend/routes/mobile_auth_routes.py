from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends
from mongo_db import get_database
from mongo_auth import hash_password, verify_password, create_access_token, get_current_user
from mongo_schemas import UserSignupRequest, UserLoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["mobile-auth"])


@router.post("/signup", response_model=TokenResponse)
async def signup(payload: UserSignupRequest):
    db = get_database()
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user_id = str(uuid4())
    await db.users.insert_one(
        {
            "_id": user_id,
            "name": payload.name.strip(),
            "email": payload.email.lower(),
            "password": hash_password(payload.password),
            "created_at": datetime.now(timezone.utc),
        }
    )
    token = create_access_token(user_id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest):
    db = get_database()
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user.get("password", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user["_id"])
    return TokenResponse(access_token=token)


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user.get("_id"),
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "created_at": current_user.get("created_at"),
    }

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.schemas import UserRegister, TokenResponse
from app.auth.service import create_user, authenticate_user
from app.core.security import create_access_token
# ✅ DEFINE ROUTER FIRST
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    return create_user(
        db=db,
        username=user.username,
        password=user.password,
        role=user.role,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    authenticated_user = authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password,
    )

    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": authenticated_user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": authenticated_user.role,
        "username": authenticated_user.username
    }
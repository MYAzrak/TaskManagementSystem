from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..security import verify_password, create_access_token
from ..crud import create_user

router = APIRouter(tags=["auth"])


@router.post(
    "/signup",
    response_model=schemas.UserOut,
    status_code=201,
    summary="Create a new user",
)
async def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.User).filter(models.User.username == payload.username).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = create_user(db, payload.username, payload.password)
    return user


@router.post(
    "/token",
    response_model=schemas.TokenOut,
    summary="Login with username/password (OAuth2 Password)",
)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token(
        {"sub": str(user.id)}, expires_delta=timedelta(minutes=60)
    )
    return {"access_token": token, "token_type": "bearer"}

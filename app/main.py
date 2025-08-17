from contextlib import asynccontextmanager
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import models
from . import schemas
from .security import verify_password, create_access_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Todo API", version="0.2.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


# ----- Auth -----


@app.post("/signup", response_model=schemas.UserOut, status_code=201)
async def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    # unique username check
    existing = (
        db.query(models.User).filter(models.User.username == payload.username).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    # create user
    from .crud import create_user

    user = create_user(db, payload.username, payload.password)
    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@app.post("/token")
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # OAuth2 password flow: username+password form fields
    user = db.query(models.User).filter(models.User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    # issue JWT
    access_token = create_access_token(
        {"sub": str(user.id)}, expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}

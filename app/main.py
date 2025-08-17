from contextlib import asynccontextmanager
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from .database import Base, engine, get_db
from . import models, schemas
from .security import verify_password, create_access_token, decode_access_token
import os

API_KEY = os.getenv("API_KEY", "123456")  # default matches the spec


tags_metadata = [
    {"name": "health", "description": "Service status checks."},
    {"name": "auth", "description": "Signup and OAuth2 password login (JWT)."},
    {
        "name": "tasks",
        "description": "User-scoped task CRUD (requires JWT and X-API-Key).",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Todo API",
    version="0.4.0",
    description="A minimal FastAPI + SQLite Todo service with JWT auth and API key.",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)


@app.get("/health", tags=["health"], summary="Service health")
async def health():
    return {"status": "ok"}


# ---------- Auth (from step 2) ----------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@app.post(
    "/signup",
    response_model=schemas.UserOut,
    status_code=201,
    tags=["auth"],
    summary="Create a new user",
    response_description="Created user (id, username)",
)
async def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.User).filter(models.User.username == payload.username).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    from .crud import create_user

    user = create_user(db, payload.username, payload.password)
    return user


@app.post(
    "/token",
    response_model=schemas.TokenOut,
    tags=["auth"],
    summary="Login with username/password (OAuth2 Password)",
    responses={401: {"description": "Invalid credentials"}},
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


# ---------- Protected deps ----------
async def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ---------- Task Endpoints (Protected) ----------
# Spec: POST /tasks, GET /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id}


@app.post(
    "/tasks",
    response_model=schemas.TaskOut,
    status_code=201,
    tags=["tasks"],
    summary="Create a task (JWT + X-API-Key)",
    response_description="The created task",
)
async def create_task(
    payload: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    task = models.Task(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        # status default = "pending" from model
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get(
    "/tasks",
    response_model=list[schemas.TaskOut],
    tags=["tasks"],
    summary="List my tasks (JWT + X-API-Key)",
)
async def list_tasks(
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    tasks = db.query(models.Task).filter(models.Task.user_id == current_user.id).all()
    return tasks


@app.get(
    "/tasks/{task_id}",
    response_model=schemas.TaskOut,
    tags=["tasks"],
    summary="Get a task by id (JWT + X-API-Key)",
    responses={404: {"description": "Task not found"}},
)
async def get_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put(
    "/tasks/{task_id}",
    response_model=schemas.TaskOut,
    tags=["tasks"],
    summary="Update task status (JWT + X-API-Key)",
    responses={404: {"description": "Task not found"}},
)
async def update_task_status(
    task_id: int,
    payload: schemas.TaskStatusUpdate,
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = payload.status
    db.commit()
    db.refresh(task)
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    tags=["tasks"],
    summary="Delete a task (JWT + X-API-Key)",
    responses={404: {"description": "Task not found"}},
)
async def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    _: None = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None

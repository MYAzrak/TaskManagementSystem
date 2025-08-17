from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, tasks

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
    version="0.5.0",
    description="A minimal FastAPI + SQLite Todo service with JWT auth and API key.",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)


@app.get("/health", tags=["health"], summary="Service health")
async def health():
    return {"status": "ok"}


# Mount routers
app.include_router(auth.router)
app.include_router(tasks.router)

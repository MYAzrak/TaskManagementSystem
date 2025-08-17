from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


# --- Task schemas ---
class TaskCreate(BaseModel):
    title: str
    description: str = ""


class TaskOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    status: Literal["pending", "completed"]
    created_at: datetime

    class Config:
        from_attributes = True


class TaskStatusUpdate(BaseModel):
    status: Literal["pending", "completed"]

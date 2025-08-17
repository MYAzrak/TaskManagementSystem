from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from datetime import datetime

# ---------- Auth / Users ----------


class UserCreate(BaseModel):
    username: str = Field(..., examples=["mya"])
    password: str = Field(..., examples=["s3cret"])
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Create a user with a unique username and password."
        }
    )


class UserOut(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)


class TokenOut(BaseModel):
    access_token: str = Field(..., examples=["<JWT>"])
    token_type: str = Field(default="bearer", examples=["bearer"])


# ---------- Tasks ----------


class TaskCreate(BaseModel):
    title: str = Field(..., examples=["Buy milk"])
    description: str = Field(default="", examples=["2% milk from the store"])
    model_config = ConfigDict(
        json_schema_extra={"description": "Create a new task (defaults to pending)."}
    )


class TaskOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    status: Literal["pending", "completed"]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TaskStatusUpdate(BaseModel):
    status: Literal["pending", "completed"] = Field(..., examples=["completed"])

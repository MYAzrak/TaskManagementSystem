from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from .database import Base


def now_utc():
    return datetime.now(timezone.utc)


class TaskStatus(str, PyEnum):
    pending = "pending"
    completed = "completed"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # ORM convenience (doesn't add columns)
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    status = Column(
        Enum(TaskStatus, native_enum=False), default=TaskStatus.pending, nullable=False
    )
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)

    owner = relationship("User", back_populates="tasks")

from sqlalchemy.orm import Session
from . import models
from .security import hash_password


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, username: str, password: str):
    user = models.User(username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

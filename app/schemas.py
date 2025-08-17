from pydantic import BaseModel


# --- Auth / User ---
class UserCreate(BaseModel):
    username: str
    password: str  # plain text in request; we'll hash it before storing


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # allows returning ORM objects

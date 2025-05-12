from pydantic import BaseModel


class CreateUser(BaseModel):
    name: str
    email: str
    avatarUrl: str
    is_logged_in: bool


class UpdateUser(BaseModel):
    id: int
    name: str
    email: str
    avatarUrl: str
    is_logged_in: bool


class User(BaseModel):
    id: int | None = None
    name: str
    email: str
    avatarUrl: str
    is_logged_in: bool

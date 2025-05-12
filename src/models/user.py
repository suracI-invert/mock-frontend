from pydantic import BaseModel


class UserInfo(BaseModel):
    id: int
    name: str
    email: str
    avatarUrl: str
    is_logged_in: bool

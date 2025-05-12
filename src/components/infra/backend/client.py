from settings import get_settings

from utils.network import get_httpx_client

from .models import CreateUser, UpdateUser, User


def build_url(path: str):
    base_url = get_settings().connection.backend_url.unicode_string()
    if path[0] == "/":
        path = path[1:]
    return f"{base_url}{path}"


def create_user(user: CreateUser):
    with get_httpx_client() as client:
        resp = client.post(
            build_url("user/v1/create"),
            json=user.model_dump(),
        )
        if resp.status_code != 200:
            raise RuntimeError("Failed to create user")
        else:
            return User.model_validate(resp.json())


def update_user(user: UpdateUser):
    with get_httpx_client() as client:
        resp = client.post(
            build_url("user/v1/update"),
            json=user.model_dump(),
        )
        if resp.status_code != 200:
            raise RuntimeError("Failed to update user")
        else:
            return User.model_validate(resp.json())


def get_user(email: str):
    with get_httpx_client() as client:
        resp = client.get(build_url(f"user/v1/{email}"))
        if resp.status_code != 200:
            raise RuntimeError("Failed to get user")
        else:
            return User.model_validate(resp.json())


def get_lessons():
    with get_httpx_client() as client:
        resp = client.get(build_url("lesson/v1/list"))
        if resp.status_code != 200:
            raise RuntimeError("Failed to get lessons")
        else:
            return resp.json()

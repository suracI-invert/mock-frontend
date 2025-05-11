from pydantic import BaseModel, HttpUrl


class ConnectionSettings(BaseModel):
    backend_url: HttpUrl

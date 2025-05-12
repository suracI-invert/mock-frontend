from contextlib import contextmanager
from pydantic import HttpUrl
import logfire
import httpx

from settings import get_settings


@contextmanager
def get_httpx_client():
    with httpx.Client(timeout=None) as client:
        logfire.instrument_httpx(client)
        yield client


def build_url(path: str):
    base_url = get_settings().connection.backend_url
    assert base_url.host
    new_url = HttpUrl.build(
        scheme=base_url.scheme,
        host=base_url.host,
        port=base_url.port,
        path=path,
    )
    return new_url.unicode_string()


def build_audio_url(audio_url: str) -> str:
    if audio_url.startswith("http"):
        return audio_url
    else:
        return build_url(f"resources/v1/audio/{audio_url}")

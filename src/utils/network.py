from contextlib import contextmanager

import logfire
import httpx


@contextmanager
def get_httpx_client():
    with httpx.Client(timeout=None) as client:
        logfire.instrument_httpx(client)

        yield client

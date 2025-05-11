FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

# RUN apt-get update && apt-get install -y libpq-dev ffmpeg libavcodec-extra

COPY .python-version .
COPY pyproject.toml .
RUN uv sync


COPY .env .
COPY config .
COPY src/ .

CMD [ "uv", "run", "fastapi", "run", "main.py"]
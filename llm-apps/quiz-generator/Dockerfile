FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

LABEL version="0.1.0"

WORKDIR /code

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_HTTP_TIMEOUT=300

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    sh -c 'for i in 1 2 3 4 5 6 7 8; do uv sync --frozen --no-install-project --no-dev && exit 0; echo "uv sync retry $i"; sleep 20; done; exit 1'

COPY . /code

RUN --mount=type=cache,target=/root/.cache/uv \
    sh -c 'for i in 1 2 3 4 5 6 7 8; do uv sync --frozen --no-dev && exit 0; echo "uv sync retry $i"; sleep 20; done; exit 1'

ENV PATH="/code/.venv/bin:$PATH"

EXPOSE 8765

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765"]

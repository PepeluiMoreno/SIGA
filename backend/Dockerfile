# syntax=docker/dockerfile:1.7

# ---- Builder ----
FROM python:3.13-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---- Runtime ----
FROM python:3.13-slim-bookworm

RUN useradd -r -u 1000 -m -d /app siga
WORKDIR /app

COPY --from=builder --chown=siga:siga /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER siga

EXPOSE 8000

CMD ["sh", "-c", "python -m app.scripts.wait_for_db && alembic upgrade head && python -m app.scripts.bootstrap && exec uvicorn main:app --host 0.0.0.0 --port 8000"]

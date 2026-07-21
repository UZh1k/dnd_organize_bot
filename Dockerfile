# ---- build stage: resolve locked production deps into an in-project venv ----
FROM python:3.12-slim AS build

# Pin uv; keep this version in sync with .github/workflows/ci.yml (setup-uv).
COPY --from=ghcr.io/astral-sh/uv:0.11.30 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/code/.venv \
    # Use the base image's Python (/usr/local/bin), not a uv-managed download,
    # so the venv copied into the runtime stage (same base image) stays valid.
    UV_PYTHON_DOWNLOADS=0

WORKDIR /code

# Only the manifest + lock are needed to build the venv, so this layer is
# cached and rebuilds only when dependencies change (not on every code edit).
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# ---- runtime stage: copy just the venv + app code ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/code/.venv/bin:$PATH"

WORKDIR /code

EXPOSE 8080

COPY --from=build /code/.venv /code/.venv
COPY ./ /code/

CMD ["bash", "-c", "alembic upgrade heads; uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4"]

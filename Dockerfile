# ---- build stage: resolve locked production deps into an in-project venv ----
FROM python:3.12-slim AS build

ENV POETRY_VERSION=2.4.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /code

# Only the manifest + lock are needed to build the venv, so this layer is
# cached and rebuilds only when dependencies change (not on every code edit).
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main

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

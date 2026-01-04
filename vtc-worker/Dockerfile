FROM python:3.13-slim AS builder
WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install poetry && \
    poetry install --without dev --no-root

FROM python:3.13-slim AS runtime
WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src ./src

ENTRYPOINT ["python"]
CMD ["src.cli", "-m", "--task-id", "88b29a34-b99d-4a3c-b17f-b60eff3ea000"]
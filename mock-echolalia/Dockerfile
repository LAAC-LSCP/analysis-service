FROM python:3.13-slim AS builder
WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry install --without dev --no-root

FROM python:3.13-slim AS runtime
WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src ./src
COPY database_1.yml .

ENTRYPOINT ["python"]
CMD ["-m", "src.cli", "--db-path", "/app/database_1.yml"]
FROM python:3.13-slim AS builder
WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-root

FROM python:3.13-slim AS runtime
WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY tests ./tests

ENTRYPOINT ["pytest"]
CMD ["-s", "-n", "auto", "tests"]
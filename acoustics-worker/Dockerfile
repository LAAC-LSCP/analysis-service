# praat-parselmouth building step frozen for arm64
FROM --platform=linux/amd64 python:3.13-slim AS poetry-builder
WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# praat-parselmouth needs a build tool
RUN apt-get update && \
    apt-get install -y build-essential cmake && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry install --no-root

FROM --platform=linux/amd64 python:3.13-slim AS runtime
WORKDIR /app

RUN apt-get update && \
    apt-get install -y sox && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=poetry-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src ./src

ENTRYPOINT ["python"]
CMD ["-m", "src.cli"]
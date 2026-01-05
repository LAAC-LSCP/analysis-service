FROM continuumio/miniconda3:latest AS conda-builder
COPY vtc/voice-type-classifier ./voice-type-classifier/
RUN cd ./voice-type-classifier && \
    conda env create -f vtc.yml

FROM python:3.13-slim AS poetry-builder
WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry install --without dev --no-root

FROM python:3.13-slim AS runtime
WORKDIR /app

RUN apt-get update && \
    apt-get install -y sox && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=poetry-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=conda-builder /opt/conda /opt/conda
COPY src ./src
COPY vtc ./vtc

ENTRYPOINT ["python"]
CMD ["-m", "src.cli"]
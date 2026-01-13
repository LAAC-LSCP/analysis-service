FROM python:3.13-slim AS repo-builder
WORKDIR /app
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/* && \
    git clone --recurse-submodules https://github.com/orasanen/ALICE/

FROM continuumio/miniconda3:latest AS conda-builder
WORKDIR /app
COPY --from=repo-builder /app/ALICE /app/ALICE/
RUN cd ./ALICE && \
    conda env create -f ALICE_Linux.yml && \
    conda env activate ALICE && \
    # This looks dumb but running ALICE will not work otherwise
    # See e.g., https://github.com/conda-forge/pytorch-cpu-feedstock/issues/350
    conda update -c conda-forge pytorch

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

COPY --from=repo-builder /app/ALICE /app/ALICE/
COPY --from=poetry-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=conda-builder /opt/conda /opt/conda
COPY src ./src

ENTRYPOINT ["python"]
CMD ["-m", "src.cli"]
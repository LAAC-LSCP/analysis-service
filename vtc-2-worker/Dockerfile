# Decided not to create a submodule and COPY but to install directly
# Otherwise had trouble with `uv sync` trying to read from
# path /app/../../.git
# Would have loved to multi-stage for uv but it's proven tricky in this case
# Final image could probably be smaller is my guess... But nothing is ever perfect :)
FROM --platform=linux/amd64 python:3.13-slim AS poetry-builder
WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry install --without dev --no-root

FROM --platform=linux/amd64 python:3.13-slim AS runtime
WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl ffmpeg git git-lfs ca-certificates && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    . $HOME/.local/bin/env && \
    rm -rf /var/lib/apt/lists/* && \
    git lfs install && \
    # TODO: add --depth 1 --shallow-submodules once we have accommodated our work for the
    # latest VTC 2 and VTC 2 repository has finally stabilised
    git clone --recurse-submodules https://github.com/LAAC-LSCP/VTC.git && \
    cd VTC && \
    # Remove the below 2 lines when above change is made
    git checkout efb6e4400bd345048740c05136dc79529daf82ad && \
    git submodule update --init --recursive && \
    uv sync

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH:/root/.local/bin"

COPY --from=poetry-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src ./src

ENTRYPOINT ["python"]
CMD ["-m", "src.cli"]
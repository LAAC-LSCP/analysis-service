import os
from typing import Generator

import pytest

from tests.app_types import RedisInfo

REDIS_HOST: str | None = os.environ.get("REDIS_HOST", None)
REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 0))


@pytest.fixture(scope="session")
def redis_host_and_port() -> Generator[RedisInfo]:
    if REDIS_HOST is None:
        raise ValueError("'REDIS_HOST' env variable is not set")

    if REDIS_PORT == 0:
        raise ValueError("'REDIS_PORT' env variable is not set")

    yield {
        "host": REDIS_HOST,
        "port": REDIS_PORT,
    }

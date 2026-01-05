import os
from enum import StrEnum
from typing import Generator

import pytest
from redis.client import PubSub
from tenacity import Retrying, stop_after_attempt, wait_fixed

from tests.app_types import RedisInfo

REDIS_HOST: str | None = os.environ.get("REDIS_HOST", None)
REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 0))


class Channels(StrEnum):
    COMPLETE_TASK = "complete_task"
    RUN_VTC = "run_vtc"


def get_next_message(
    pubsub: PubSub, max_attempts: int = 60, wait_seconds: float = 1
) -> dict:
    """
    Looks for next message, for testing purposes
    """
    for attempt in Retrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_fixed(wait_seconds),
        reraise=True,
    ):
        with attempt:
            message = pubsub.get_message(timeout=1, ignore_subscribe_messages=True)

            if message:
                return message
            else:
                raise Exception("Retrying...")

    raise TimeoutError("No messages found")


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

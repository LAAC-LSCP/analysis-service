import os
from typing import TypedDict

REDIS_HOST: str | None = os.environ.get("REDIS_HOST", None)
REDIS_PORT: int | None = int(os.environ.get("REDIS_PORT", None))


class RedisInfo(TypedDict):
    host: str
    port: int


def get_redis_host_and_port() -> RedisInfo:
    if REDIS_HOST is None:
        raise ValueError("'REDIS_HOST' env variable is not set")
    
    if REDIS_PORT is None:
        raise ValueError("'REDIS_PORT' env variable is not set")

    return {
        "host": REDIS_HOST,
        "port": REDIS_PORT,
    }

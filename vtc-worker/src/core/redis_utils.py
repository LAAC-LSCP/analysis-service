import os
from typing import TypedDict

REDIS_HOST: str | None = os.environ.get("REDIS_HOST", None)
REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 0))


class RedisInfo(TypedDict):
    host: str
    port: int


def get_redis_host_and_port() -> RedisInfo:
    redis_host = REDIS_HOST
    redis_port = REDIS_PORT

    if redis_host is None:
        print("'REDIS_HOST' env variable is not set, using 'localhost'")

        redis_host = "localhost"

    if redis_port == 0:
        print("'REDIS_PORT' env variable is not set, using '6379'")

        redis_port = 6379

    return {
        "host": redis_host,
        "port": redis_port,
    }

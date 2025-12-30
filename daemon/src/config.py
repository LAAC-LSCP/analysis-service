from typing import TypedDict

REDIS_HOST = "localhost"
REDIS_PORT = 6379


class RedisInfo(TypedDict):
    host: str
    port: int


def get_redis_host_and_port() -> RedisInfo:
    return {
        "host": REDIS_HOST,
        "port": REDIS_PORT,
    }

import subprocess

import pytest
import redis
from tenacity import retry, stop_after_delay

from src import config


def start_redis_if_down():
    try:
        r = redis.Redis(**config.get_redis_host_and_port())
        r.ping()
    except redis.ConnectionError:
        subprocess.run(["redis-server", "--daemonize", "yes"], check=False)

        wait_for_redis_to_come_up()


@retry(stop=stop_after_delay(10))
def wait_for_redis_to_come_up():
    r = redis.Redis(**config.get_redis_host_and_port())

    return r.ping()


def clear_redis_data():
    r = redis.Redis(**config.get_redis_host_and_port())
    r.flushall()
    r.connection_pool.disconnect()


def shutdown_redis():
    try:
        subprocess.run(["redis-cli", "shutdown"], check=False)
    except Exception:
        pass


@pytest.fixture(scope="function")
def restart_redis_pubsub():
    start_redis_if_down()
    clear_redis_data()

    yield

    shutdown_redis()

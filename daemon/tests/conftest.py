import subprocess
import uuid
from datetime import datetime
from typing import Generator, Optional, Protocol

import pytest
import redis
from tenacity import retry, stop_after_delay

from src import redis_utils
from src.core.echolalia_api import Task
from src.core.types import Operation, TaskStatus


def start_redis_if_down():
    try:
        r = redis.Redis(**redis_utils.get_redis_host_and_port())
        r.ping()
    except redis.ConnectionError:
        subprocess.run(["redis-server", "--daemonize", "yes"], check=False)

        wait_for_redis_to_come_up()


@retry(stop=stop_after_delay(10))
def wait_for_redis_to_come_up():
    r = redis.Redis(**redis_utils.get_redis_host_and_port())

    return r.ping()


def clear_redis_data():
    r = redis.Redis(**redis_utils.get_redis_host_and_port())
    r.flushall()
    r.connection_pool.disconnect()


def shutdown_redis():
    try:
        subprocess.run(["redis-cli", "shutdown"], check=False)
    except Exception:
        pass


class TaskFactory(Protocol):
    def __call__(
        self,
        task_id: Optional[uuid.UUID] = None,
        model_name: Optional[Operation] = None,
        status_label: Optional[TaskStatus] = None,
        user_id: Optional[uuid.UUID] = None,
        dataset_name: Optional[str] = None,
        dataset_id_label: Optional[str] = None,
        created: Optional[datetime] = None,
        modified: Optional[datetime] = None,
    ) -> Task: ...


@pytest.fixture(scope="session")
def task_factory() -> Generator[TaskFactory, None, None]:
    def factory(
        task_id: Optional[uuid.UUID] = None,
        model_name: Optional[Operation] = None,
        status_label: TaskStatus | None = None,
        user_id: Optional[uuid.UUID] = None,
        dataset_name: Optional[str] = None,
        dataset_id_label: Optional[str] = None,
        created: Optional[datetime] = None,
        modified: Optional[datetime] = None,
    ) -> Task:
        return Task(
            task_uid=task_id or uuid.uuid4(),
            model_name=model_name or Operation.VTC,
            status_label=status_label or TaskStatus.PENDING,
            user_uid=user_id or uuid.uuid4(),
            dataset_name=dataset_name or "",
            dataset_uid_label=dataset_id_label or "",
            created=created or datetime.now(),
            modified=modified or datetime.now(),
        )

    yield factory


@pytest.fixture(scope="function")
def restart_redis_pubsub() -> Generator[None]:
    start_redis_if_down()
    clear_redis_data()

    yield

    shutdown_redis()

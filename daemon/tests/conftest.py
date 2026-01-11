import uuid
from datetime import datetime
from typing import Generator, Optional, Protocol

import pytest
from analysis_service_core.src.redis.commands import Operation

from src.core.echolalia_api import Task
from src.core.types import TaskStatus


class TaskFactory(Protocol):
    def __call__(
        self,
        task_id: Optional[uuid.UUID] = None,
        model_name: Optional[Operation] = None,
        status_label: Optional[TaskStatus] = None,
        user_id: Optional[uuid.UUID] = None,
        dataset_name: Optional[str] = None,
        dataset_uid_label: Optional[str] = None,
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
        dataset_uid_label: Optional[str] = None,
        created: Optional[datetime] = None,
        modified: Optional[datetime] = None,
    ) -> Task:
        return Task(
            task_uid=task_id or uuid.uuid4(),
            model_name=model_name or Operation.RUN_VTC,
            status_label=status_label or TaskStatus.PENDING,
            user_uid=user_id or uuid.uuid4(),
            dataset_name=dataset_name or "",
            dataset_uid_label=dataset_uid_label or "",
            created=created or datetime.now(),
            modified=modified or datetime.now(),
        )

    yield factory

"""
This file contains the different response formats/types expected
from the Echolalia external endpoints
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Set, TypedDict
from uuid import UUID

from analysis_service_core.src.redis.commands import Operation

from src.core.types import TaskStatus

type Tasks = Set["Task"]
type Statuses = Set["Status"]


class AuthResponse(TypedDict):
    access_token: str
    expires_in: int
    token_type: str


class Status(TypedDict):
    pk_nc_analysis_status_type: int
    label: str
    uid_label: TaskStatus
    modified: datetime
    created: datetime


class PutPayload(TypedDict):
    status: TaskStatus
    estimated_duration: int


@dataclass
class Task:
    task_uid: UUID
    model_name: Operation
    status_label: TaskStatus
    user_uid: UUID
    dataset_name: str
    dataset_uid_label: str
    created: datetime
    modified: datetime

    @classmethod
    def from_dict(self, task: dict) -> "Task":
        return Task(
            task_uid=UUID(task["task_uid"]),
            model_name=Operation(task["model_name"]),
            status_label=TaskStatus(task["status_label"].lower()),
            user_uid=UUID(task["user_uid"]),
            dataset_name=task["dataset_name"],
            dataset_uid_label=task["dataset_uid_label"],
            created=datetime.fromisoformat(task["created"]),
            modified=datetime.fromisoformat(task["modified"]),
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Task):
            raise ValueError("Cannot compare task with non-task object")

        return self.task_uid == other.task_uid

    def __hash__(self) -> int:
        return hash(self.task_uid)

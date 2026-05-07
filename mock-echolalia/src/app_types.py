from enum import StrEnum
from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel


class Task(BaseModel):
    task_uid: UUID
    model_name: str
    status_label: Literal["pending", "running", "completed"]
    user_uid: UUID
    dataset_name: str
    dataset_uid_label: str
    created: str  # TODO: work with datetimes
    modified: str
    estimated_duration: int


class Database(BaseModel):
    tasks: List[Task]


class FlaskConfig(StrEnum):
    TOKENS = "TOKENS"
    TASK_DB = "TASK_DB"

from enum import StrEnum
from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel


class Task(BaseModel):
    uuid: UUID
    status: Literal["PENDING", "RUNNING", "COMPLETED"]
    estimated_duration: int


class Database(BaseModel):
    tasks: List[Task]


class FlaskConfig(StrEnum):
    TOKENS = "TOKENS"
    TASK_DB = "TASK_DB"

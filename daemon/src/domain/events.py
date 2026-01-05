from abc import ABC
from dataclasses import dataclass
from uuid import UUID


class Event(ABC):
    task_id: UUID

    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(self, dict_repr: dict) -> "Event":
        raise NotImplementedError


@dataclass
class TaskStarted(Event):
    task_id: UUID

    def to_dict(self) -> dict:
        return {"task_id": str(self.task_id)}

    @classmethod
    def from_dict(self, dict_repr: dict) -> "TaskStarted":
        return TaskStarted(task_id=UUID(dict_repr["task_id"]))


@dataclass
class TaskCompleted(Event):
    task_id: UUID

    def to_dict(self) -> dict:
        return {"task_id": str(self.task_id)}

    @classmethod
    def from_dict(self, dict_repr: dict) -> "TaskCompleted":
        return TaskCompleted(task_id=UUID(dict_repr["task_id"]))

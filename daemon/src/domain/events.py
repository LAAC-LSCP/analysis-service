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
class TaskCreated(Event):
    task_id: UUID

    def to_dict(self) -> dict:
        return {"task_id": str(self.task_id)}

    @classmethod
    def from_dict(self, dict_repr: dict) -> "TaskCreated":
        return TaskCreated(task_id=UUID(dict_repr["task_id"]))

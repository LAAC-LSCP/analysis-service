from abc import ABC
from dataclasses import dataclass
from uuid import UUID


class Command(ABC):
    task_id: UUID

    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(self, dict_repr: dict) -> "Command":
        raise NotImplementedError


@dataclass
class CreateTask(Command):
    task_id: UUID

    def to_dict(self) -> dict:
        return {
            "task_id": str(self.task_id),
        }

    @classmethod
    def from_dict(self, dict_repr: dict) -> "CreateTask":
        return CreateTask(task_id=UUID(dict_repr["task_id"]))

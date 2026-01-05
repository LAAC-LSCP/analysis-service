from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal
from uuid import UUID


# NOTE: need to always define this the same as the Daemon's channel names
class ChannelName(StrEnum):
    COMPLETE_TASK = "complete_task"
    RUN_VTC = "run_vtc"


class Command(ABC):
    task_id: UUID

    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(self, dict_repr: dict) -> "Command":
        raise NotImplementedError


# NOTE: need to always define this as defined in Daemon's command module
@dataclass
class RunTask(Command):
    task_id: UUID
    dataset_uid_label: str
    operation: Literal["vtc"]

    def to_dict(self) -> dict:
        return {
            "task_id": str(self.task_id),
            "dataset_uid_label": self.dataset_uid_label,
            "operation": str(self.operation),
        }

    @classmethod
    def from_dict(self, dict_repr: dict) -> "RunTask":
        return RunTask(
            task_id=UUID(dict_repr["task_id"]),
            dataset_uid_label=dict_repr["dataset_uid_label"],
            operation=dict_repr["operation"],
        )


@dataclass
class CompleteTask(Command):
    task_id: UUID

    def to_dict(self) -> dict:
        return {
            "task_id": str(self.task_id),
        }

    @classmethod
    def from_dict(self, dict_repr: dict) -> "CompleteTask":
        return CompleteTask(
            task_id=UUID(dict_repr["task_id"]),
        )

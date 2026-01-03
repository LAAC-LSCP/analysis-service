from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


# NOTE: need to always define this the same as the Daemon's channel names
class ChannelName(StrEnum):
    COMPLETE_TASK = "complete_task"


# NOTE: need to always define this as defined in Daemon's command module
@dataclass
class RunTask:
    task_id: UUID

    def to_dict(self) -> dict:
        return {
            "task_id": str(self.task_id),
        }

    @classmethod
    def from_dict(self, dict_repr: dict) -> "RunTask":
        return RunTask(task_id=UUID(dict_repr["task_id"]))

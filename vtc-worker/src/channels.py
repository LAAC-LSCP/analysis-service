from enum import StrEnum
from typing import TypedDict
from uuid import UUID


# NOTE: need to always define this the same as the Daemon's channel names
class ChannelName(StrEnum):
    RUN_VTC = "run_vtc"
    COMPLETE_TASK = "complete_task"


# NOTE: need to always define this the same as the Daemon command
class RunTask(TypedDict):
    task_id: UUID

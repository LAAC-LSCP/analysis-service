import json
from uuid import UUID

import redis

from src.core.channels import ChannelName, RunTask


def run_vtc(r: redis.Redis, task_id: UUID) -> None:
    message = RunTask(task_id=task_id)

    r.publish(
        ChannelName.COMPLETE_TASK,
        json.dumps(message.to_dict()),
    )

    return

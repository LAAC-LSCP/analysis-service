import json
from uuid import UUID

import pytest
import redis

from src.core import redis_utils
from src.core.channels import ChannelName, RunTask
from src.core.run_vtc import run_vtc


@pytest.mark.usefixtures("restart_redis_pubsub")
def test_run_vtc_sends_to_redis():
    r = redis.Redis(**redis_utils.get_redis_host_and_port())
    id = UUID("88b29a34-b99d-4a3c-b17f-b60eff3ea000")
    pubsub = r.pubsub()
    pubsub.subscribe(ChannelName.COMPLETE_TASK)

    run_vtc(r, task_id=id)
    message = pubsub.get_message(timeout=1.0, ignore_subscribe_messages=True)

    data = RunTask.from_dict(json.loads(message["data"].decode("utf-8")))
    assert data == RunTask(task_id=id)

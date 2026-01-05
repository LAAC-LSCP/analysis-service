import json

import redis

from tests.app_types import RedisInfo
from tests.conftest import Channels, get_next_message


def test_vtc_start_to_finish(redis_host_and_port: RedisInfo):
    """Test VTC workflow from task submission to completion"""
    r = redis.Redis(host=redis_host_and_port["host"], port=redis_host_and_port["port"])

    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(Channels.COMPLETE_TASK)

    print("Waiting for completion message...")
    message = get_next_message(pubsub)

    data = json.loads(message["data"].decode("utf-8"))

    assert data.get("task_id") == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

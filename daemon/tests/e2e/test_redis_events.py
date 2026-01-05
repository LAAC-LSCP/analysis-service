import json
from uuid import UUID

import pytest
import redis

from src import redis_utils
from src.domain import events
from src.service.queue.channels import ChannelName, get_channels
from src.service.service import Service
from tests.fake_event_handlers import EventTester
from tests.unit.service.fake_http_client import FakeHTTPClient


@pytest.mark.usefixtures("restart_redis_pubsub")
def test_redis_updates_lead_to_handler_calls():
    r = redis.Redis(**redis_utils.get_redis_host_and_port())

    event_handlers = {
        events.TaskStarted: [lambda event: None],
        events.TaskCompleted: [lambda event: None],
    }
    event_tester = EventTester(event_handlers)
    http_client = FakeHTTPClient()

    service = Service(r, get_channels(), event_tester.event_handlers, http_client)

    r.publish(
        ChannelName.RUN_VTC,
        json.dumps({"task_id": "c611e347-2c08-4909-b174-0e76a678ce57"}),
    )

    service.get_next_message_and_handle()

    assert len(event_tester.calls) == 1
    assert event_tester.calls[0]["type"] == events.TaskStarted
    assert event_tester.calls[0]["message"] == events.TaskStarted(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57")
    )

    r.publish(
        ChannelName.COMPLETE_TASK,
        json.dumps({"task_id": "c611e347-2c08-4909-b174-0e76a678ce57"}),
    )

    service.get_next_message_and_handle()

    assert len(event_tester.calls) == 2
    assert event_tester.calls[1]["type"] == events.TaskCompleted
    assert event_tester.calls[1]["message"] == events.TaskCompleted(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57")
    )

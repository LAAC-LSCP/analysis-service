from uuid import UUID

import pytest
import redis

from src import redis_utils
from src.core.types import TaskStatus
from src.domain import events
from src.service.handlers.event_handlers import get_event_handlers
from src.service.handlers.types import EventHandlers
from src.service.queue.channels import get_channels
from src.service.service import Service
from tests.conftest import TaskFactory
from tests.fake_event_handlers import EventTester
from tests.unit.service.fake_http_client import FakeHTTPClient


@pytest.mark.usefixtures("restart_redis_pubsub")
def test_service_get_new_task(task_factory: TaskFactory):
    """Test if the service finds new tasks and puts them
    on Redis, retrieved and handled"""
    http_client = FakeHTTPClient(
        results=[
            {
                task_factory(
                    task_id=UUID("70a1acc6-f5fd-44ea-8b41-bc4b3e4cfc02"),
                    status_label=TaskStatus.PENDING,
                ),
            }
        ]
    )
    r = redis.Redis(**redis_utils.get_redis_host_and_port())

    event_handlers: EventHandlers = get_event_handlers(FakeHTTPClient)  # type: ignore
    event_tester = EventTester(event_handlers)

    service = Service(r, get_channels(), event_tester.event_handlers, http_client)

    service.tick()
    service.get_next_message_and_handle()

    assert len(event_tester.calls) == 2
    assert event_tester.calls[0]["type"] == events.TaskStarted
    assert event_tester.calls[0]["handler_name"] == "handle_task_created"
    assert event_tester.calls[0]["message"] == events.TaskStarted(
        task_id=UUID("70a1acc6-f5fd-44ea-8b41-bc4b3e4cfc02")
    )
    assert event_tester.calls[1]["type"] == events.TaskStarted
    assert event_tester.calls[1]["handler_name"] == "send_update"
    assert event_tester.calls[1]["message"] == events.TaskStarted(
        task_id=UUID("70a1acc6-f5fd-44ea-8b41-bc4b3e4cfc02")
    )

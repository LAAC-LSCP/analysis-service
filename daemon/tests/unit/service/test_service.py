from uuid import UUID

import analysis_service_core.src.redis.commands as commands
from analysis_service_core.src.redis.channels import get_channels
from analysis_service_core.testing.mocks import PubSubMock

from src.core.types import TaskStatus
from src.service.command_handlers import get_command_handlers
from src.service.service import Service
from tests.command_tester import CommandTester
from tests.conftest import TaskFactory
from tests.unit.service.fake_http_client import FakeHTTPClient


def test_service_get_new_task(task_factory: TaskFactory):
    """Test if the service finds new tasks and puts them
    on Redis, retrieved and handled"""
    http_client = FakeHTTPClient(
        results=[
            {
                task_factory(
                    task_id=UUID("70a1acc6-f5fd-44ea-8b41-bc4b3e4cfc02"),
                    status_label=TaskStatus.PENDING,
                    dataset_uid_label="my-dataset_4cafe10b-f91c-4f80-9b8c-61fb7fbf8901",
                ),
            }
        ]
    )
    command_handlers = get_command_handlers(FakeHTTPClient)  # type: ignore
    command_tester = CommandTester(command_handlers)

    service = Service(
        PubSubMock(subscribe_to=list(get_channels().channel_names)),
        get_channels(),
        command_tester.command_handlers,
        http_client,
    )

    service.tick()
    service.get_next_message_and_handle()

    assert len(command_tester.calls) == 2
    assert command_tester.calls[0]["type"] == commands.RunTask
    assert command_tester.calls[0]["handler_name"] == "handle_run_task"
    assert command_tester.calls[0]["message"] == commands.RunTask(
        task_id=UUID("70a1acc6-f5fd-44ea-8b41-bc4b3e4cfc02"),
        operation="vtc",
        dataset_uid_label="my-dataset_4cafe10b-f91c-4f80-9b8c-61fb7fbf8901",
    )
    assert command_tester.calls[1]["type"] == commands.RunTask
    assert command_tester.calls[1]["handler_name"] == "send_update"
    assert command_tester.calls[1]["message"] == commands.RunTask(
        task_id=UUID("70a1acc6-f5fd-44ea-8b41-bc4b3e4cfc02"),
        operation="vtc",
        dataset_uid_label="my-dataset_4cafe10b-f91c-4f80-9b8c-61fb7fbf8901",
    )

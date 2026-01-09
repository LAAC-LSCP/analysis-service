from typing import Tuple
from uuid import UUID

import analysis_service_core.src.redis.commands as commands
import pytest

# TODO: fix this channels mess when we add queues
from analysis_service_core.src.redis.channels import (
    ChannelDict,
    ChannelName,
    Channels,
)
from analysis_service_core.testing.mocks.pubsub import PubSubMock

from src.core.types import TaskStatus
from src.service.command_handlers import get_command_handlers
from src.service.service import Service
from tests.command_tester import CommandTester
from tests.conftest import TaskFactory
from tests.unit.service.fake_http_client import FakeHTTPClient


@pytest.fixture
def service_tester(
    task_factory: TaskFactory,
) -> Tuple[Service, CommandTester, PubSubMock]:
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

    channels = Channels(
        {
            ChannelDict(
                name=ChannelName.COMPLETE_TASK,
                command=commands.CompleteTask,
            ),
        }
    )

    pubsub = PubSubMock(subscribe_to=list(channels.channel_names))
    command_handlers = get_command_handlers(http_client, pubsub)  # type: ignore
    command_tester = CommandTester(command_handlers)

    return (
        Service(
            pubsub,
            channels,
            command_tester.command_handlers,
            http_client,  # type: ignore
        ),
        command_tester,
        pubsub,
    )


def test_service_task_lifecycle(
    service_tester: Tuple[Service, CommandTester, PubSubMock],
):
    """Test if the service finds new tasks and puts them
    on Redis, retrieved and handled"""
    service, command_tester, pubsub = service_tester
    service.tick()

    assert len(command_tester.calls) == 2
    assert command_tester.calls[0]["type"] == commands.RunTask
    assert command_tester.calls[0]["handler_name"] == "send_request"
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

    pubsub.publish(
        channel_name=ChannelName.COMPLETE_TASK,
        cmd=commands.CompleteTask(
            task_id=UUID("70a1acc6-f5fd-44ea-8b41-bc4b3e4cfc02"),
        ),
    )
    service.get_next_message_and_handle()

    assert len(command_tester.calls) == 3
    assert command_tester.calls[2]["handler_name"] == "send_update"
    assert command_tester.calls[2]["message"] == commands.CompleteTask(
        task_id=UUID("70a1acc6-f5fd-44ea-8b41-bc4b3e4cfc02"),
    )

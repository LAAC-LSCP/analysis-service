from uuid import UUID

import analysis_service_core.src.redis.commands as commands
from analysis_service_core.src.redis.channels import ChannelName, get_channels
from analysis_service_core.testing.mocks.pubsub import PubSubMock

from src.service.service import Service
from tests.command_tester import CommandTester
from tests.unit.service.fake_http_client import FakeHTTPClient


def test_redis_updates_lead_to_handler_calls():
    command_handlers = {
        commands.RunTask: [lambda event: None],
        commands.CompleteTask: [lambda event: None],
    }
    command_tester = CommandTester(command_handlers)
    http_client = FakeHTTPClient()

    pubsub = PubSubMock(subscribe_to=list(get_channels().channel_names))
    service = Service(
        pubsub, get_channels(), command_tester.command_handlers, http_client
    )

    pubsub.publish(
        ChannelName.RUN_VTC,
        commands.RunTask(
            task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
            dataset_uid_label="",
            operation=commands.Operation.RUN_VTC,
        ),
    )

    service.get_next_message_and_handle()

    assert len(command_tester.calls) == 1
    assert command_tester.calls[0]["type"] == commands.RunTask
    assert command_tester.calls[0]["message"] == commands.RunTask(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
        dataset_uid_label="",
        operation=commands.Operation.RUN_VTC,
    )

    pubsub.publish(
        ChannelName.COMPLETE_TASK,
        commands.CompleteTask(task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57")),
    )

    service.get_next_message_and_handle()

    assert len(command_tester.calls) == 2
    assert command_tester.calls[1]["type"] == commands.CompleteTask
    assert command_tester.calls[1]["message"] == commands.CompleteTask(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57")
    )

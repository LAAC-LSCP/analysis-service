from uuid import UUID

import analysis_service_core.src.redis.commands as commands
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mocks.queue import QueueMock

from src.service.service import Service
from tests.command_tester import CommandTester
from tests.unit.service.fake_http_client import FakeHTTPClient, Task, TaskStatus


def test_service():
    command_handlers = {
        commands.RunTask: [lambda event: None],
        commands.CompleteTask: [lambda event: None],
    }
    command_tester = CommandTester(command_handlers)
    http_client = FakeHTTPClient(
        [
            {
                Task(
                    task_uid=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
                    model_name=commands.Operation.RUN_VTC,
                    status_label=TaskStatus.PENDING,
                    user_uid="",
                    dataset_name="",
                    dataset_uid_label="",
                    created=None,
                    modified=None,
                ),
            }
        ]
    )

    completion_queue = QueueMock(QueueName.COMPLETE_TASK)
    service = Service(completion_queue, command_tester.command_handlers, http_client)

    service.tick()

    assert len(command_tester.calls) == 1
    assert command_tester.calls[0]["type"] == commands.RunTask
    assert command_tester.calls[0]["message"] == commands.RunTask(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
        dataset_uid_label="",
        operation=commands.Operation.RUN_VTC,
    )

    completion_queue.enqueue(
        commands.CompleteTask(task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57")),
    )

    service.get_completion_message_and_handle()

    assert len(command_tester.calls) == 2
    assert command_tester.calls[1]["type"] == commands.CompleteTask
    assert command_tester.calls[1]["message"] == commands.CompleteTask(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57")
    )

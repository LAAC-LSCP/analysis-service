from datetime import datetime, timedelta
from uuid import UUID

import analysis_service_core.src.redis.commands as commands
from analysis_service_core.src.redis.pubsub import ChannelName
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mocks.pubsub import PubSubMock
from analysis_service_core.testing.mocks.queue import QueueMock

from src.service.service import Service
from tests.command_tester import CommandTester
from tests.unit.service.fake_http_client import FakeHTTPClient, Task, TaskStatus


def _make_service(http_client, command_handlers):
    command_tester = CommandTester(command_handlers)
    completion_queue = QueueMock(QueueName.COMPLETE_TASK)
    fail_queue = QueueMock(QueueName.FAIL_TASK)
    progress_bus = PubSubMock(subscribe_to=[ChannelName.UPDATE_STATUS])
    service = Service(
        completion_queue,
        progress_bus,
        command_tester.command_handlers,
        http_client,
        fail_queue,
    )

    return service, command_tester, completion_queue, fail_queue, progress_bus


def test_service():
    command_handlers = {
        commands.RunTask: [lambda event: None],
        commands.CompleteTask: [lambda event: None],
        commands.FailTask: [lambda event: None],
        commands.ReportProgress: [lambda event: None],
    }
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

    service, command_tester, completion_queue, _, progress_bus = _make_service(
        http_client, command_handlers
    )

    service.tick()

    assert len(command_tester.calls) == 1
    assert command_tester.calls[0]["type"] == commands.RunTask
    assert command_tester.calls[0]["message"] == commands.RunTask(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
        dataset_uid_label="",
        operation=commands.Operation.RUN_VTC,
        resume=False,
    )

    completion_queue.enqueue(
        commands.CompleteTask(task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57")),
    )
    progress_bus.publish(
        ChannelName.UPDATE_STATUS,
        commands.ReportProgress(
            task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
            completed_progress=1.0,
            completed_pass_effort=10.0,
            partial_pass_progress=0.0,
            partial_pass_effort=0.0,
            total_effort=10.0,
            completed_passes=1,
            total_passes=1,
        ),
    )

    service.get_completion_message_and_handle()
    service._listen_and_handle_progress()

    assert len(command_tester.calls) == 3
    assert command_tester.calls[1]["type"] == commands.CompleteTask
    assert command_tester.calls[1]["message"] == commands.CompleteTask(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57")
    )
    assert command_tester.calls[2]["type"] == commands.ReportProgress
    assert command_tester.calls[2]["message"] == commands.ReportProgress(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
        completed_progress=1.0,
        completed_pass_effort=10.0,
        partial_pass_progress=0.0,
        partial_pass_effort=0.0,
        total_effort=10.0,
        completed_passes=1,
        total_passes=1,
    )


def test_fail_task_message_is_handled():
    command_handlers = {
        commands.FailTask: [lambda event: None],
    }
    service, command_tester, _, fail_queue, _ = _make_service(
        FakeHTTPClient([set()]), command_handlers
    )

    fail_queue.enqueue(
        commands.FailTask(
            task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
            reason="All 2 igroup(s) failed to process.",
        )
    )

    service.get_fail_message_and_handle()

    assert len(command_tester.calls) == 1
    assert command_tester.calls[0]["type"] == commands.FailTask
    assert command_tester.calls[0]["message"] == commands.FailTask(
        task_id=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
        reason="All 2 igroup(s) failed to process.",
    )


def test_tick_fails_stale_running_task_using_floor_when_no_duration():
    command_handlers = {
        commands.RunTask: [lambda event: None],
        commands.FailTask: [lambda event: None],
    }
    stale_task = Task(
        task_uid=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
        model_name=commands.Operation.RUN_VTC,
        status_label=TaskStatus.RUNNING,
        user_uid="",
        dataset_name="",
        dataset_uid_label="",
        created=datetime.now() - timedelta(seconds=Service.STALE_TASK_FLOOR_S + 60),
        modified=datetime.now() - timedelta(seconds=Service.STALE_TASK_FLOOR_S + 60),
    )
    service, command_tester, _, _, _ = _make_service(
        FakeHTTPClient([{stale_task}]), command_handlers
    )

    service.tick()

    fail_calls = [c for c in command_tester.calls if c["type"] == commands.FailTask]
    assert len(fail_calls) == 1
    assert fail_calls[0]["message"].task_id == stale_task.task_uid


def test_tick_does_not_fail_running_task_within_budget():
    command_handlers = {
        commands.RunTask: [lambda event: None],
        commands.FailTask: [lambda event: None],
    }
    fresh_task = Task(
        task_uid=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
        model_name=commands.Operation.RUN_VTC,
        status_label=TaskStatus.RUNNING,
        user_uid="",
        dataset_name="",
        dataset_uid_label="",
        created=datetime.now(),
        modified=datetime.now(),
    )
    service, command_tester, _, _, _ = _make_service(
        FakeHTTPClient([{fresh_task}]), command_handlers
    )

    service.tick()

    assert not any(c["type"] == commands.FailTask for c in command_tester.calls)


def test_tick_uses_duration_based_budget_when_available():
    command_handlers = {
        commands.RunTask: [lambda event: None],
        commands.FailTask: [lambda event: None],
    }
    # 10 hours of audio / 60 => ~10 minute budget, well over the floor.
    duration_seconds = 10 * 3600
    budget_s = duration_seconds * Service.STALE_TASK_DURATION_FACTOR
    stale_task = Task(
        task_uid=UUID("c611e347-2c08-4909-b174-0e76a678ce57"),
        model_name=commands.Operation.RUN_VTC,
        status_label=TaskStatus.RUNNING,
        user_uid="",
        dataset_name="",
        dataset_uid_label="",
        created=datetime.now() - timedelta(seconds=budget_s + 60),
        modified=datetime.now() - timedelta(seconds=budget_s + 60),
        duration_seconds=duration_seconds,
    )
    within_budget_task = Task(
        task_uid=UUID("6906ebf8-2836-484a-9420-7923e1a3f79c"),
        model_name=commands.Operation.RUN_VTC,
        status_label=TaskStatus.RUNNING,
        user_uid="",
        dataset_name="",
        dataset_uid_label="",
        created=datetime.now() - timedelta(seconds=budget_s - 60),
        modified=datetime.now() - timedelta(seconds=budget_s - 60),
        duration_seconds=duration_seconds,
    )
    service, command_tester, _, _, _ = _make_service(
        FakeHTTPClient([{stale_task, within_budget_task}]), command_handlers
    )

    service.tick()

    fail_calls = [c for c in command_tester.calls if c["type"] == commands.FailTask]
    assert len(fail_calls) == 1
    assert fail_calls[0]["message"].task_id == stale_task.task_uid

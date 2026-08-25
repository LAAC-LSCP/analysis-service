from time import monotonic
from typing import Any, Dict, List, Protocol, Type, TypeVar
from uuid import UUID

import analysis_service_core.src.redis.commands as commands
from analysis_service_core.src.logger import LoggerFactory
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.core.types import TaskStatus
from src.service.http_client import HTTPClient

logger = LoggerFactory.get_logger(__name__)

CommandT = TypeVar("CommandT", bound=commands.Command, contravariant=True)


class CommandHandler(Protocol[CommandT]):
    def __call__(self, command: CommandT) -> None: ...


type CommandHandlers = Dict[Type[commands.Command], List[CommandHandler[Any]]]

# Workers report progress after every igroup, which can mean many messages per second
# for large datasets. ELSI doesn't need that resolution, so updates are throttled to
# at most one per task within this window (a generous cap since tasks rarely finish
# in lockstep). The final update (progress >= 1.0) always goes through.
PROGRESS_UPDATE_MIN_INTERVAL_S = 5.0


def update_elsi_status(
    http_client: HTTPClient, task_status: TaskStatus
) -> CommandHandler:
    def send_status_update(command: commands.Command) -> None:
        http_client.put_task(
            command.task_id,
            payload={
                "status": task_status,
                "estimated_duration": 0,
            },
        )

        logger.info(f"Sent update to ELSI for task \
{command.task_id!s} with status '{task_status!s}' and \
estimated duration '{0}'")

    return send_status_update


def report_task_failure(http_client: HTTPClient) -> CommandHandler:
    def send_failure(command: commands.Command) -> None:
        assert isinstance(command, commands.FailTask)

        http_client.put_task(
            command.task_id,
            payload={
                "status": TaskStatus.FAILED,
                "estimated_duration": 0,
            },
        )

        logger.info(
            f"Sent update to ELSI for task {command.task_id!s} with status "
            f"'{TaskStatus.FAILED!s}'. Reason: {command.reason}"
        )

    return send_failure


def update_elsi_progress(
    http_client: HTTPClient, min_interval_s: float = PROGRESS_UPDATE_MIN_INTERVAL_S
) -> CommandHandler:
    last_sent_at: Dict[UUID, float] = {}

    def send_progress_update(command: commands.ReportProgress) -> None:
        is_complete = command.completed_progress >= 1.0
        now = monotonic()
        last = last_sent_at.get(command.task_id)

        if last is not None and not is_complete and (now - last) < min_interval_s:
            return

        last_sent_at[command.task_id] = now

        http_client.put_task(
            command.task_id,
            payload={
                "status": TaskStatus.RUNNING,
                "progress": command.completed_progress,
            },
        )

        logger.info(
            f"Sent progress update to ELSI for task {command.task_id!s}: "
            f"{command.completed_progress:.1%}"
        )

    return send_progress_update


def handle_run_task(queues: Dict[QueueName, Queue]) -> CommandHandler:
    def send_request(command: commands.RunTask) -> None:
        logger.info(
            f"Sending request to broker for task with model: {command.operation!s}"
        )
        queue: Queue | None = None
        if command.operation == commands.Operation.RUN_VTC:
            queue = queues[QueueName.RUN_VTC]
        elif command.operation == commands.Operation.RUN_ALICE:
            queue = queues[QueueName.RUN_ALICE]
        elif command.operation == commands.Operation.RUN_ACOUSTICS:
            queue = queues[QueueName.RUN_ACOUSTICS]
        elif command.operation == commands.Operation.RUN_VTC_2:
            queue = queues[QueueName.RUN_VTC_2]
        elif command.operation == commands.Operation.RUN_W2V2:
            queue = queues[QueueName.RUN_W2V2]
        elif command.operation == commands.Operation.RUN_TEST_MODEL:
            queue = queues[QueueName.RUN_TEST_MODEL]

        if queue is None:
            return

        queue.enqueue(command)

    return send_request


def get_command_handlers(
    http_client: HTTPClient, queues: Dict[QueueName, Queue]
) -> CommandHandlers:
    return {
        commands.RunTask: [
            handle_run_task(queues),
            update_elsi_status(http_client, TaskStatus.RUNNING),
        ],
        commands.CompleteTask: [update_elsi_status(http_client, TaskStatus.COMPLETED)],
        commands.FailTask: [report_task_failure(http_client)],
        commands.ReportProgress: [update_elsi_progress(http_client)],
    }

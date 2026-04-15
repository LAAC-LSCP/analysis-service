from typing import Any, Dict, List, Protocol, Type, TypeVar

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


def update_elsi_progress(http_client: HTTPClient) -> CommandHandler:
    def send_progress_update(command: commands.ReportProgress) -> None:
        #       TODO: NOT IMPLEMENTED
        #       logger.info(f"Sent progress update to ELSI for task \
        # {command.task_id!s} with progress {command.progress!s}")
        pass

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
        commands.ReportProgress: [update_elsi_progress(http_client)],
    }

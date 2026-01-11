from typing import Any, Dict, List, Protocol, Type, TypeVar

import analysis_service_core.src.redis.commands as commands
from analysis_service_core.src.redis.channels import ChannelName
from analysis_service_core.src.redis.pubsub import PubSub

from src.core.types import TaskStatus
from src.service.http_client import HTTPClient

CommandT = TypeVar("CommandT", bound=commands.Command, contravariant=True)


class CommandHandler(Protocol[CommandT]):
    def __call__(self, command: CommandT) -> None: ...


type CommandHandlers = Dict[Type[commands.Command], List[CommandHandler[Any]]]


def update_echolalia(
    http_client: HTTPClient, task_status: TaskStatus
) -> CommandHandler:
    def send_update(command: commands.Command) -> None:
        http_client.put_task(
            command.task_id,
            payload={
                "status": task_status,
                "estimated_duration": 0,
            },
        )

        print(
            f"Sent update to Echolalia for task \
{str(command.task_id)} with status '{str(task_status)}' and \
estimated duration '{0}'"
        )

    return send_update


def handle_run_task(pubsub: PubSub) -> CommandHandler:
    def send_request(command: commands.RunTask) -> None:
        print(f"Sending request to redis for task with model: {str(command.operation)}")
        if command.operation == commands.Operation.RUN_VTC:
            pubsub.publish(ChannelName.RUN_VTC, command)
        elif command.operation == commands.Operation.RUN_ALICE:
            pubsub.publish(ChannelName.RUN_ALICE, command)
        elif command.operation == commands.Operation.RUN_ACOUSTICS:
            pubsub.publish(ChannelName.RUN_ACOUSTICS, command)
        elif command.operation == commands.Operation.RUN_VTC_2:
            pubsub.publish(ChannelName.RUN_VTC_2, command)

    return send_request


def get_command_handlers(http_client: HTTPClient, pubsub: PubSub) -> CommandHandlers:
    return {
        commands.RunTask: [
            handle_run_task(pubsub),
            update_echolalia(http_client, TaskStatus.RUNNING),
        ],
        commands.CompleteTask: [update_echolalia(http_client, TaskStatus.COMPLETED)],
    }

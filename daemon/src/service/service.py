import asyncio
from datetime import datetime, timedelta
from typing import Type

from analysis_service_core.src.model import RunTask
from analysis_service_core.src.redis.channels import Channels
from analysis_service_core.src.redis.commands import Command
from analysis_service_core.src.redis.pubsub import PubSub
from tenacity import Retrying, stop_after_attempt, wait_fixed

from src.core.types import TaskStatus
from src.service.command_handlers import CommandHandlers
from src.service.http_client import HTTPClient


class Service:
    S_PER_UPDATE: int = 10

    _channels: Channels
    _command_handlers: CommandHandlers
    _http_client: HTTPClient
    _pubsub: PubSub

    def __init__(
        self,
        pubsub: PubSub,
        channels: Channels,
        command_handlers: CommandHandlers,
        http_client: HTTPClient,
    ):
        self._pubsub = pubsub
        self._channels = channels
        self._command_handlers = command_handlers
        self._http_client = http_client

    async def start(self) -> None:
        print("Daemon started")
        loop = asyncio.get_event_loop()
        redis_task = loop.run_in_executor(None, self._listen_and_handle_redis)
        api_task = self._external_api_loop()

        await asyncio.gather(redis_task, api_task)

    async def _external_api_loop(self) -> None:
        while True:
            current_t = datetime.now()

            print("Loading new tasks...")
            self.tick()

            sleep_t: float = (
                current_t + timedelta(seconds=self.S_PER_UPDATE) - datetime.now()
            ).total_seconds()

            await asyncio.sleep(sleep_t if sleep_t > 0 else 0)

    def tick(self) -> None:
        all_tasks = self._http_client.get_all_tasks()

        new_tasks = {
            task for task in all_tasks if task.status_label == TaskStatus.PENDING
        }

        if len(new_tasks) != 0:
            print(f"Received new tasks: {new_tasks}")

        for task in new_tasks:
            message: RunTask = RunTask(
                task_id=task.task_uid,
                dataset_uid_label=task.dataset_uid_label,
                operation=task.model_name,
            )

            print(f"Publishing task with id '{task.task_uid}' to redis")
            for handler in self._command_handlers.get(RunTask, []):
                handler(message)

    def _listen_and_handle_redis(self) -> None:
        for message in self._pubsub.listen():
            self._handle_message(message)

    def get_next_message_and_handle(
        self, max_attempts: int = 3, wait_seconds: float = 0.1
    ) -> None:
        """
        Looks for next message, mostly for testing purposes
        """
        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_fixed(wait_seconds),
            reraise=True,
        ):
            with attempt:
                message = self._pubsub.get_message(timeout=1)

                if message:
                    self._handle_message(message)

                    return
                else:
                    raise Exception("Retrying...")

        return

    def _handle_message(self, message: dict) -> None:
        print(f"Handling message: {message}")
        channel_name = self._pubsub.get_channel_from_message(message)
        data = self._pubsub.get_data_from_message(message)

        command_cls: Type[Command] | None = next(
            (
                channel.command
                for channel in self._channels.channels
                if channel.name.value == channel_name
            ),
            None,
        )
        if command_cls is None:
            raise ValueError("Command not associated with a channel")

        self._handle_cmd(command_cls, data)

    def _handle_cmd(self, command_cls: Type[Command], data: dict) -> None:
        command = command_cls.from_dict(dict_repr=data)

        for handler in self._command_handlers.get(command_cls, []):
            handler(command)

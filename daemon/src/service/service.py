import asyncio
import json
from datetime import datetime, timedelta
from typing import Type

from redis import Redis
from tenacity import Retrying, stop_after_attempt, wait_fixed

from src.core.types import TaskStatus
from src.domain.commands import RunTask
from src.domain.events import Event
from src.service.handlers.types import EventHandlers
from src.service.http_client import HTTPClient
from src.service.queue.channels import ChannelName, Channels


class Service:
    S_PER_UPDATE: int = 10

    _channels: Channels
    _r: Redis
    _event_handlers: EventHandlers
    _http_client: HTTPClient

    def __init__(
        self,
        r: Redis,
        channels: Channels,
        event_handlers: EventHandlers,
        http_client: HTTPClient,
    ):
        self._pubsub = r.pubsub(ignore_subscribe_messages=True)
        self._pubsub.subscribe(*tuple(channels.channel_names))

        self._r = r
        self._channels = channels
        self._event_handlers = event_handlers
        self._http_client = http_client

    async def start(self) -> None:
        loop = asyncio.get_event_loop()
        redis_task = loop.run_in_executor(None, self._listen_and_handle_redis)
        api_task = self._external_api_loop()

        await asyncio.gather(redis_task, api_task)

    async def _external_api_loop(self) -> None:
        while True:
            current_t = datetime.now()

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

        for task in new_tasks:
            message: RunTask = RunTask(task_id=task.task_uid)

            self._r.publish(ChannelName.RUN_VTC, json.dumps(message.to_dict()))

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
                message = self._pubsub.get_message(timeout=1, ignore_subscribe_messages=True)

                if message:
                    self._handle_message(message)

                    return
                else:
                    raise Exception("Retrying...")

        return

    def _handle_message(self, message: dict) -> None:
        channel_name = message["channel"].decode("utf-8")
        data = json.loads(message["data"].decode("utf-8"))

        event_cls: Type[Event] | None = next(
            (
                channel.event
                for channel in self._channels.channels
                if channel.name.value == channel_name
            ),
            None,
        )
        if event_cls is None:
            raise ValueError("Event not associated with a channel")

        self._handle_event(event_cls, data)

    def _handle_event(self, event_cls: Type[Event], data: dict) -> None:
        event = event_cls.from_dict(dict_repr=data)

        for handler in self._event_handlers.get(event_cls, []):
            handler(event)

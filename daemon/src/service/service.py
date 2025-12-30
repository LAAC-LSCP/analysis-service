import json
from typing import Type

from redis import Redis
from tenacity import Retrying, stop_after_attempt, wait_fixed

from src.domain.events import Event
from src.service.handlers.types import EventHandlers
from src.service.queue.channels import Channels


class Service:
    _channels: Channels
    _r: Redis
    _event_handlers: EventHandlers

    def __init__(self, r: Redis, channels: Channels, event_handlers: EventHandlers):
        channel_names = {channel.name.value for channel in channels}

        self._pubsub = r.pubsub(ignore_subscribe_messages=True)
        self._pubsub.subscribe(*tuple(channel_names))

        self._channels = channels
        self._event_handlers = event_handlers

    def start(self) -> None:
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

    def stop(self) -> None:
        self._pubsub.close()

    def _handle_message(self, message: dict) -> None:
        channel_name = message["channel"].decode("utf-8")
        data = json.loads(message["data"].decode("utf-8"))

        event_cls: Type[Event] | None = next(
            (
                channel.event
                for channel in self._channels
                if channel.name.value == channel_name
            ),
            None,
        )
        if event_cls is None:
            raise ValueError("Event not associated with a channel")

        self._handle_event(event_cls, data)

    def _handle_event(self, event_cls: Type[Event], data: dict) -> None:
        event = event_cls(**data)

        for handler in self._event_handlers.get(event_cls, []):
            handler(event)

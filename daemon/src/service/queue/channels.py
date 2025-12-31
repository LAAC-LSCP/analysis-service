from dataclasses import dataclass
from enum import StrEnum
from typing import Set, Type

import src.domain.events as events


class ChannelName(StrEnum):
    CREATE_TASK = "create_task"


@dataclass(frozen=True)
class ChannelDict:
    name: ChannelName
    event: Type[events.Event]


class Channels:
    """
    Wrapper for Redis channel management
    """

    _channels: Set[ChannelDict]

    def __init__(self, channels: Set[ChannelDict]):
        self._channels = channels

    @property
    def channel_names(self) -> Set[str]:
        return {channel.name for channel in self._channels}

    @property
    def events(self) -> Set[Type[events.Event]]:
        return {channel.event for channel in self._channels}

    @property
    def channels(self) -> Set[ChannelDict]:
        return self._channels


def get_channels() -> Channels:
    return Channels(
        {
            ChannelDict(
                name=ChannelName.CREATE_TASK,
                event=events.TaskCreated,
            ),
        }
    )

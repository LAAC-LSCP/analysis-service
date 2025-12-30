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


Channels = Set[ChannelDict]


def get_channels() -> Channels:
    return {
        ChannelDict(
            name=ChannelName.CREATE_TASK,
            event=events.TaskCreated,
        ),
    }

from typing import Any, Dict, List, Protocol, Type, TypeVar

from src.domain import events

EventT = TypeVar("EventT", bound=events.Event, contravariant=True)


class EventHandler(Protocol[EventT]):
    def __call__(self, event: EventT) -> None: ...


type EventHandlers = Dict[Type[events.Event], List[EventHandler[Any]]]

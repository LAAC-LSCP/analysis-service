from typing import List, Type, TypedDict

import src.domain.events as events
from src.service.handlers.types import EventHandler, EventHandlers


class Call(TypedDict):
    type: Type[events.Event]
    message: events.Event
    handler_name: str
    threw_error: bool


class EventTester:
    """
    Generic spy class for events

    Wraps events in such a way that it records information about
    event calls, e.g., name of handler or whether an error was thrown
    """

    _calls: List[Call]
    _event_handlers: EventHandlers

    def __init__(self, event_handlers: EventHandlers):
        self._calls = []
        self._event_handlers = {
            event: [self._track_event_handler(event, handler) for handler in handlers]
            for event, handlers in event_handlers.items()
        }

    def _track_event_handler(
        self, event_cls: Type[events.Event], handler: EventHandler
    ) -> EventHandler:
        def _call_event(event: events.Event) -> None:
            threw_error = False

            try:
                handler(event)
            except Exception:
                threw_error = True
            finally:
                call = Call(
                    type=event_cls,
                    message=event,
                    handler_name=str(handler.__name__),  # type: ignore
                    threw_error=threw_error,
                )
                self._calls.append(call)

        return _call_event

    @property
    def event_handlers(self) -> EventHandlers:
        return self._event_handlers

    @property
    def calls(self) -> List[Call]:
        return self._calls

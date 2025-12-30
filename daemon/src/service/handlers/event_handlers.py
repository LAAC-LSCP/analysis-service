from src.domain import events
from src.service.handlers.types import EventHandlers


def handle_task_created(event: events.TaskCreated) -> None:
    print(f"Task with id '{event.task_id}' created!")


def get_event_handlers() -> EventHandlers:
    return {events.TaskCreated: [handle_task_created]}

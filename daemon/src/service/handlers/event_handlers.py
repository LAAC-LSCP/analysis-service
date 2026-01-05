from src.core.types import TaskStatus
from src.domain import events
from src.service.handlers.types import EventHandler, EventHandlers
from src.service.http_client import HTTPClient


def update_echolalia(http_client: HTTPClient, task_status: TaskStatus) -> EventHandler:
    def send_update(event: events.Event) -> None:
        http_client.put_task(
            event.task_id,
            payload={
                "status": task_status,
                "estimated_duration": 0,
            },
        )

        print(
            f"Sent update to Echolalia for task \
{str(event.task_id)} with status '{str(task_status)}' and \
estimated duration '{0}'"
        )

    return send_update


def handle_task_created(event: events.TaskStarted) -> None:
    print(f"Task with id '{event.task_id}' created!")


def get_event_handlers(http_client: HTTPClient) -> EventHandlers:
    return {
        events.TaskStarted: [
            handle_task_created,
            update_echolalia(http_client, TaskStatus.RUNNING),
        ],
        events.TaskCompleted: [update_echolalia(http_client, TaskStatus.COMPLETED)],
    }

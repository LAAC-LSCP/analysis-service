from dataclasses import dataclass
from uuid import UUID


class Event:
    task_id: UUID


@dataclass
class TaskCreated(Event):
    task_id: UUID

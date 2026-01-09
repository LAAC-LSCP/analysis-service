from typing import List, Optional
from uuid import UUID

from src.core.echolalia_api import PutPayload, Task, Tasks
from src.core.types import TaskStatus


class FakeHTTPClient:
    """
    Fake HTTP Client
    Everytime the fake client is called it cycles over the results
    supplied in the constructor
    """

    _results: List[Tasks]
    _counter: int

    def __init__(self, results: Optional[List[Tasks]] = None):
        self._counter = 0
        self._results = results or []

    def get_all_tasks(self) -> Tasks:
        idx: int = self._counter % len(self._results)

        self._counter += 1

        return self._results[idx]

    def get_task_by_id(self, id: UUID) -> Optional[Task]:
        idx: int = self._counter % len(self._results)

        self._counter += 1

        return next(
            (result for result in self._results[idx] if result.task_uid == id), None
        )

    def get_all_tasks_with_status(self, status: TaskStatus) -> Tasks:
        idx: int = self._counter % len(self._results)

        self._counter += 1

        return {
            result for result in self._results[idx] if result.status_label == status
        }

    def put_task(self, task_id: UUID, payload: PutPayload) -> None:
        self._results = [
            {
                self._set_status(t, payload["status"]) if t.task_uid == task_id else t
                for t in r
            }
            for r in self._results
        ]

        return

    def _append_task(self, result: List[Task], task: Task) -> List[Task]:
        result += [task]

        return result

    def _set_status(self, task: Task, status: TaskStatus) -> Task:
        task.status_label = status

        return task

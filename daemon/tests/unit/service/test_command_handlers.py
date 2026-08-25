from typing import List, Tuple
from uuid import UUID

import analysis_service_core.src.redis.commands as commands

from src.core.elsi_api import PutPayload
from src.core.types import TaskStatus
from src.service.command_handlers import update_elsi_progress


class SpyHTTPClient:
    def __init__(self):
        self.calls: List[Tuple[UUID, PutPayload]] = []

    def put_task(self, task_id: UUID, payload: PutPayload) -> None:
        self.calls.append((task_id, payload))


def _progress(task_id: UUID, completed_progress: float) -> commands.ReportProgress:
    return commands.ReportProgress(
        task_id=task_id,
        completed_progress=completed_progress,
        completed_pass_effort=0.0,
        partial_pass_progress=0.0,
        partial_pass_effort=0.0,
        total_effort=1.0,
        completed_passes=0,
        total_passes=1,
    )


def test_progress_update_sends_status_and_progress_without_estimated_duration():
    http_client = SpyHTTPClient()
    handler = update_elsi_progress(http_client)
    task_id = UUID("c611e347-2c08-4909-b174-0e76a678ce57")

    handler(_progress(task_id, 0.5))

    assert len(http_client.calls) == 1
    sent_task_id, payload = http_client.calls[0]
    assert sent_task_id == task_id
    assert payload["status"] == TaskStatus.RUNNING
    assert payload["progress"] == 0.5
    assert "estimated_duration" not in payload


def test_progress_updates_are_throttled_per_task():
    http_client = SpyHTTPClient()
    handler = update_elsi_progress(http_client, min_interval_s=100.0)
    task_id = UUID("c611e347-2c08-4909-b174-0e76a678ce57")

    handler(_progress(task_id, 0.3))
    handler(_progress(task_id, 0.4))
    handler(_progress(task_id, 0.5))

    assert len(http_client.calls) == 1
    assert http_client.calls[0][1]["progress"] == 0.3


def test_final_progress_update_bypasses_throttle():
    http_client = SpyHTTPClient()
    handler = update_elsi_progress(http_client, min_interval_s=100.0)
    task_id = UUID("c611e347-2c08-4909-b174-0e76a678ce57")

    handler(_progress(task_id, 0.3))
    handler(_progress(task_id, 1.0))

    assert len(http_client.calls) == 2
    assert http_client.calls[1][1]["progress"] == 1.0


def test_progress_updates_are_throttled_independently_per_task():
    http_client = SpyHTTPClient()
    handler = update_elsi_progress(http_client, min_interval_s=100.0)
    task_a = UUID("c611e347-2c08-4909-b174-0e76a678ce57")
    task_b = UUID("6906ebf8-2836-484a-9420-7923e1a3f79c")

    handler(_progress(task_a, 0.3))
    handler(_progress(task_b, 0.6))

    assert len(http_client.calls) == 2

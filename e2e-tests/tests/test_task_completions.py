import time

import pytest
import requests
from analysis_service_core.src.config import Config

TASK_ID = "f1a2b3c4-d5e6-7890-abcd-ef1234567890"
TIMEOUT = 120
POLL_INTERVAL = 5


@pytest.fixture
def get_task(config: Config, authentication_token: str):
    def _get_task(task_id: str) -> dict | None:
        url = f"{config.get('BASE_URL')}/analytics/services/tasks/{task_id}"
        resp = requests.get(
            url, headers={"Authorization": f"Bearer {authentication_token}"}
        )
        if resp.status_code == 404:
            return None
        return resp.json()

    return _get_task


def test_test_model_task_completes(get_task):
    """Assert the test_model task reaches 'completed' status within TIMEOUT seconds."""
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        task = get_task(TASK_ID)
        if task and task.get("status_label") == "completed":
            return
        time.sleep(POLL_INTERVAL)

    pytest.fail(f"Task '{TASK_ID}' did not complete within {TIMEOUT}s")

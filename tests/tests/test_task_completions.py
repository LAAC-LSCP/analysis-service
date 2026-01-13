import time

import pytest
import requests
from analysis_service_core.src.config import Config


@pytest.fixture
def get_task(config: Config, authentication_token: str):
    def _get_task(task_id) -> dict | None:
        task_url = (
            f"{config.get('BASE_URL')}/api/analytics/services/tasks/{str(task_id)}"
        )
        headers = {"Authorization": f"Bearer {authentication_token}"}
        resp = requests.get(task_url, headers=headers)

        if resp.status_code == 404:
            return None

        return resp.json()

    return _get_task


@pytest.mark.parametrize(
    "task_id,model_name",
    [
        ("2111e290-128f-4c21-b7cc-2318f54b63ce", "acoustics"),
        ("a1b2c3d4-e5f6-7890-abcd-ef1234567890", "vtc"),
        ("954f493c-443f-498c-9490-7b7036e4b1be", "vtc-2"),
        ("cea95657-8e73-4a97-a982-44368d9a835c", "alice"),
    ],
)
def test_model_completion(task_id: str, model_name: str, get_task):
    timeout = 100
    poll_interval = 5
    start_time = time.time()

    found = False

    while time.time() - start_time < timeout:
        task = get_task(task_id)

        if task is None or not task.get("status_label") == "completed":
            time.sleep(poll_interval)

            continue

        found = True
        break

    assert (
        found
    ), f"{model_name} task '{task_id}' not completed within {timeout} seconds"

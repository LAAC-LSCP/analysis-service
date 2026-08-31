from datetime import timezone

from src.core.elsi_api import Task

_BASE_TASK_DICT = {
    "task_uid": "c611e347-2c08-4909-b174-0e76a678ce57",
    "model_name": "vtc",
    "status_label": "RUNNING",
    "user_uid": "6906ebf8-2836-484a-9420-7923e1a3f79c",
    "dataset_name": "some-dataset",
    "dataset_uid_label": "some-dataset-uid",
    "created": "2026-08-31T10:00:00",
    "modified": "2026-08-31T10:00:00",
}


def test_from_dict_assumes_utc_for_naive_timestamps():
    task = Task.from_dict(_BASE_TASK_DICT)

    assert task.created.tzinfo is not None
    assert task.modified.tzinfo is not None
    assert task.created.utcoffset().total_seconds() == 0
    assert task.modified.utcoffset().total_seconds() == 0


def test_from_dict_preserves_explicit_timezone():
    task_dict = {
        **_BASE_TASK_DICT,
        "created": "2026-08-31T10:00:00+02:00",
        "modified": "2026-08-31T10:00:00+02:00",
    }

    task = Task.from_dict(task_dict)

    assert task.modified.tzinfo is not None
    assert task.modified.astimezone(timezone.utc).hour == 8

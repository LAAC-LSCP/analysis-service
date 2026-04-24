from pathlib import Path
from uuid import UUID

import pytest
from analysis_service_core.src.config import Config
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mocks.queue import QueueMock

from tests.unit.w2v2_mock import W2V2Mock


@pytest.fixture
def w2v2_mock(tmp_path_factory: pytest.TempPathFactory) -> W2V2Mock:
    queue = QueueMock(QueueName.RUN_VTC)
    config = Config(check_required=False)
    config.set("W2V2_FOLDER", tmp_path_factory.mktemp("w2v2_folder", numbered=True))

    return W2V2Mock(queue, config, skip_moving_files=True)


def test_w2v2_inputs_outputs(
    w2v2_mock: W2V2Mock,
    flat_dataset_tmp: Path,
) -> None:
    """
    Tests the input-output behaviour of run model on flat datasets
    """
    output_dir = flat_dataset_tmp / "outputs"
    w2v2_mock.run_model(
        dataset_dir=flat_dataset_tmp,
        output_dir=output_dir,
        task_id=UUID("00000000-0000-0000-0000-000000000000"),
    )

    output_files_and_folders = {f for f in output_dir.rglob("*")}

    assert len(output_files_and_folders) == 5

    output_files = {f for f in output_files_and_folders if f.is_file()}

    assert output_files == {
        output_dir / "output" / "raw" / "recording_1.csv",
        output_dir / "output" / "raw" / "recording_2.csv",
        output_dir / "output" / "raw" / "recording_3.csv",
    }


def test_w2v2_inputs_outputs_nested(
    w2v2_mock: W2V2Mock,
    nested_dataset_tmp: Path,
) -> None:
    """
    Tests the input-output behaviour of run model on nested datasets
    """
    output_dir = nested_dataset_tmp / "outputs"
    w2v2_mock.run_model(
        dataset_dir=nested_dataset_tmp,
        output_dir=output_dir,
        task_id=UUID("00000000-0000-0000-0000-000000000000"),
    )

    output_files_and_folders = {f for f in output_dir.rglob("*")}

    assert len(output_files_and_folders) == 8

    output_files = {f for f in output_files_and_folders if f.is_file()}

    assert len(output_files) == 6

    assert output_files == {
        output_dir / "output" / "raw" / "child_2_day_1_recording.csv",
        output_dir / "output" / "raw" / "child_1_day_1_hour_1_recording.csv",
        output_dir / "output" / "raw" / "child_1_day_2_recording.csv",
        output_dir / "output" / "raw" / "child_2_day_1_hour_1_recording.csv",
        output_dir / "output" / "raw" / "child_1_day_1_recording.csv",
        output_dir / "output" / "raw" / "child_2_day_1_hour_2_recording.csv",
    }

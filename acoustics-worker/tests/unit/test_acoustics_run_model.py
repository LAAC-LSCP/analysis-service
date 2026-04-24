from pathlib import Path
from uuid import UUID

import pytest
from analysis_service_core.src.config import Config
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mocks.queue import QueueMock

from tests.unit.acoustics_mock import AcousticsMock


@pytest.fixture
def acoustics_mock(tmp_path_factory: pytest.TempPathFactory) -> AcousticsMock:
    queue = QueueMock(QueueName.RUN_VTC)
    config = Config(check_required=False)
    config.set("VTC_FOLDER", tmp_path_factory.mktemp("vtc_folder", numbered=True))

    return AcousticsMock(queue, config, skip_moving_files=True)


def test_acoustics_inputs_outputs(
    acoustics_mock: AcousticsMock,
    flat_dataset_tmp: Path,
) -> None:
    """
    Tests the input-output behaviour of run model on flat datasets
    """
    output_dir = flat_dataset_tmp / "outputs"
    acoustics_mock.run_model(
        dataset_dir=flat_dataset_tmp,
        output_dir=output_dir,
        task_id=UUID("00000000-0000-0000-0000-000000000000"),
    )

    output_files_and_folders = {f for f in output_dir.rglob("**")}

    assert len(output_files_and_folders) == 5

    output_files = {f for f in output_files_and_folders if f.is_file()}

    assert output_files == {
        output_dir / "raw" / "recording_1.csv",
        output_dir / "raw" / "recording_2.csv",
        output_dir / "raw" / "recording_3.csv",
    }


def test_acoustics_inputs_outputs_nested(
    acoustics_mock: AcousticsMock,
    nested_dataset_tmp: Path,
) -> None:
    """
    Tests the input-output behaviour of run model on nested datasets
    """
    output_dir = nested_dataset_tmp / "outputs"
    acoustics_mock.run_model(
        dataset_dir=nested_dataset_tmp,
        output_dir=output_dir,
        task_id=UUID("00000000-0000-0000-0000-000000000000"),
    )

    output_files_and_folders = {f for f in output_dir.rglob("*")}

    assert len(output_files_and_folders) == 15

    output_files = {f for f in output_files_and_folders if f.is_file()}

    assert len(output_files) == 6

    assert output_files == {
        output_dir / "raw" / "child_2" / "day_1" / "recording.csv",
        output_dir / "raw" / "child_1" / "day_1" / "hour_1" / "recording.csv",
        output_dir / "raw" / "child_1" / "day_2" / "recording.csv",
        output_dir / "raw" / "child_2" / "day_1" / "hour_1" / "recording.csv",
        output_dir / "raw" / "child_1" / "day_1" / "recording.csv",
        output_dir / "raw" / "child_2" / "day_1" / "hour_2" / "recording.csv",
    }

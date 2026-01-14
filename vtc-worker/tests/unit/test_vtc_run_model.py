from pathlib import Path

import pytest
from analysis_service_core.src.config import Config
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mocks.queue import QueueMock

from tests.unit.vtc_mock import VTC_Mock


@pytest.fixture
def vtc_mock(tmp_path_factory: pytest.TempPathFactory) -> VTC_Mock:
    queue = QueueMock(QueueName.RUN_VTC)
    config = Config(check_required=False)
    config.set("VTC_FOLDER", tmp_path_factory.mktemp("vtc_folder", numbered=True))

    return VTC_Mock(queue, config, skip_moving_files=True)


def test_vtc_inputs_outputs(
    vtc_mock: VTC_Mock,
    flat_dataset_tmp: Path,
) -> None:
    """
    Tests the input-output behaviour of run model on flat datasets
    """
    output_dir = flat_dataset_tmp / "outputs"
    vtc_mock.run_model(dataset_dir=flat_dataset_tmp, output_dir=output_dir)

    output_files_and_folders = {f for f in output_dir.rglob("*")}

    assert len(output_files_and_folders) == 4

    output_files = {f for f in output_files_and_folders if f.is_file()}

    assert output_files == {
        output_dir / "raw" / "recording_1.rttm",
        output_dir / "raw" / "recording_2.rttm",
        output_dir / "raw" / "recording_3.rttm",
    }


def test_vtc_inputs_outputs_nested(
    vtc_mock: VTC_Mock,
    nested_dataset_tmp: Path,
) -> None:
    """
    Tests the input-output behaviour of run model on nested datasets
    """
    output_dir = nested_dataset_tmp / "outputs"
    vtc_mock.run_model(dataset_dir=nested_dataset_tmp, output_dir=output_dir)

    output_files_and_folders = {f for f in output_dir.rglob("*")}

    assert len(output_files_and_folders) == 15

    output_files = {f for f in output_files_and_folders if f.is_file()}

    assert len(output_files) == 6

    assert output_files == {
        output_dir / "raw" / "child_2" / "day_1" / "recording.rttm",
        output_dir / "raw" / "child_1" / "day_1" / "hour_1" / "recording.rttm",
        output_dir / "raw" / "child_1" / "day_2" / "recording.rttm",
        output_dir / "raw" / "child_2" / "day_1" / "hour_1" / "recording.rttm",
        output_dir / "raw" / "child_1" / "day_1" / "recording.rttm",
        output_dir / "raw" / "child_2" / "day_1" / "hour_2" / "recording.rttm",
    }

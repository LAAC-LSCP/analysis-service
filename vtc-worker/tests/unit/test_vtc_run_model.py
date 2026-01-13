from pathlib import Path

import pytest
from analysis_service_core.src.config import Config
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mocks.queue import QueueMock

from tests.unit.vtc_mock import VTC_Mock


@pytest.fixture
def vtc_mock() -> VTC_Mock:
    queue = QueueMock(QueueName.RUN_VTC)
    config = Config(check_required=False)
    config.set("VTC_FOLDER", Path("."))  # We don't need this

    return VTC_Mock(queue, config, skip_moving_files=True)


def test_vtc_inputs_outputs(
    vtc_mock: VTC_Mock,
    flat_dataset_tmp: Path,
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """
    Tests the input-output behaviour of run model on flat datasets
    """
    tmp_path = tmp_path_factory.mktemp("test_vtc", True)
    vtc_mock.run_model(dataset_dir=flat_dataset_tmp, output_dir=tmp_path)

    output_files_and_folders = {f for f in tmp_path.rglob("*")}

    assert len(output_files_and_folders) == 3
    assert output_files_and_folders == {
        tmp_path / "recording_1.rttm",
        tmp_path / "recording_2.rttm",
        tmp_path / "recording_3.rttm",
    }


def test_vtc_inputs_outputs_nested(
    vtc_mock: VTC_Mock,
    nested_dataset_tmp: Path,
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """
    Tests the input-output behaviour of run model on nested datasets
    """
    tmp_path = tmp_path_factory.mktemp("test_vtc", True)
    vtc_mock.run_model(dataset_dir=nested_dataset_tmp, output_dir=tmp_path)

    output_files_and_folders = {f for f in tmp_path.rglob("*")}

    assert len(output_files_and_folders) == 14

    output_files = {f for f in output_files_and_folders if f.is_file()}

    assert len(output_files) == 6

    assert output_files == {
        tmp_path / "child_2" / "day_1" / "recording.rttm",
        tmp_path / "child_1" / "day_1" / "hour_1" / "recording.rttm",
        tmp_path / "child_1" / "day_2" / "recording.rttm",
        tmp_path / "child_2" / "day_1" / "hour_1" / "recording.rttm",
        tmp_path / "child_1" / "day_1" / "recording.rttm",
        tmp_path / "child_2" / "day_1" / "hour_2" / "recording.rttm",
    }

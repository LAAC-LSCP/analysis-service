from pathlib import Path

import pytest
from analysis_service_core.src.config import Config
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mocks.queue import QueueMock

from tests.unit.alice_mock import ALICE_Mock


@pytest.fixture
def alice_mock(tmp_path_factory: pytest.TempPathFactory) -> ALICE_Mock:
    queue = QueueMock(QueueName.RUN_ALICE)
    config = Config(check_required=False)
    config.set("ALICE_FOLDER", tmp_path_factory.mktemp("alice_folder", numbered=True))
    config.set("CONDA_ACTIVATE_FILE", "")
    config.set("CONDA_ENV_NAME", "")

    return ALICE_Mock(queue, config, skip_moving_files=True)


def test_alice_inputs_outputs(
    alice_mock: ALICE_Mock,
    flat_dataset_tmp: Path,
) -> None:
    """
    Tests the input-output behaviour of run model on flat datasets
    """
    output_dir = flat_dataset_tmp / "outputs"
    alice_mock.run_model(dataset_dir=flat_dataset_tmp, output_dir=output_dir)

    output_files_and_folders = {f for f in output_dir.rglob("*")}

    assert len(output_files_and_folders) == 9

    output_files = {f for f in output_files_and_folders if f.is_file()}

    assert len(output_files) == 6

    assert output_files == {
        output_dir / "output" / "raw" / "recording_1.txt",
        output_dir / "output" / "extra" / "recording_1_sum.txt",
        output_dir / "output" / "raw" / "recording_2.txt",
        output_dir / "output" / "extra" / "recording_2_sum.txt",
        output_dir / "output" / "raw" / "recording_3.txt",
        output_dir / "output" / "extra" / "recording_3_sum.txt",
    }


def test_alice_inputs_outputs_nested(
    alice_mock: ALICE_Mock,
    nested_dataset_tmp: Path,
) -> None:
    """
    Tests the input-output behaviour of run model on nested datasets
    """
    output_dir = nested_dataset_tmp / "outputs"
    alice_mock.run_model(dataset_dir=nested_dataset_tmp, output_dir=output_dir)

    output_files_and_folders = {f for f in output_dir.rglob("*")}

    assert len(output_files_and_folders) == 33

    output_files = {f for f in output_files_and_folders if f.is_file()}

    assert len(output_files) == 12

    # In fact, I don't think we have any nested ALICE data. Whether this is correct
    # is debatable, but it's a generalization of what we have for flat datasets
    assert output_files == {
        output_dir / "output" / "child_2" / "day_1" / "raw" / "recording.txt",
        output_dir / "output" / "child_2" / "day_1" / "extra" / "recording_sum.txt",
        output_dir
        / "output"
        / "child_1"
        / "day_1"
        / "hour_1"
        / "raw"
        / "recording.txt",
        output_dir
        / "output"
        / "child_1"
        / "day_1"
        / "hour_1"
        / "extra"
        / "recording_sum.txt",
        output_dir / "output" / "child_1" / "day_2" / "raw" / "recording.txt",
        output_dir / "output" / "child_1" / "day_2" / "extra" / "recording_sum.txt",
        output_dir
        / "output"
        / "child_2"
        / "day_1"
        / "hour_1"
        / "raw"
        / "recording.txt",
        output_dir
        / "output"
        / "child_2"
        / "day_1"
        / "hour_1"
        / "extra"
        / "recording_sum.txt",
        output_dir / "output" / "child_1" / "day_1" / "raw" / "recording.txt",
        output_dir / "output" / "child_1" / "day_1" / "extra" / "recording_sum.txt",
        output_dir
        / "output"
        / "child_2"
        / "day_1"
        / "hour_2"
        / "raw"
        / "recording.txt",
        output_dir
        / "output"
        / "child_2"
        / "day_1"
        / "hour_2"
        / "extra"
        / "recording_sum.txt",
    }

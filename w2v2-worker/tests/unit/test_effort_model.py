from pathlib import Path

from analysis_service_core.src.filesystem import UUID, get_final_output_dir

from tests.unit.effort_model_mock import W2V2EffortModelMock


class TestEffortModelFlatDataset:
    effort_model = W2V2EffortModelMock()
    task_id = UUID("94d1754b-9ce6-435a-b81e-89de666ef3a8")

    def test_find_input_groups(self, flat_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(flat_dataset_tmp)

        assert len(input_groups) == 1
        assert input_groups == [
            [flat_dataset_tmp / "recordings" / "converted" / "standard"]
        ]

    def test_ogroup_from_igroup(self, flat_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(flat_dataset_tmp)

        assert len(input_groups) == 1

        output_folder = get_final_output_dir(flat_dataset_tmp, self.task_id)

        output_group = self.effort_model.ogroup_from_igroup(
            flat_dataset_tmp, input_groups[0], output_folder
        )

        assert len(output_group) == 3
        assert set(output_group) == {
            output_folder / "output" / "raw" / "recording_1.csv",
            output_folder / "output" / "raw" / "recording_2.csv",
            output_folder / "output" / "raw" / "recording_3.csv",
        }

    def test_calculate_progress(self, flat_dataset_tmp: Path):
        output_folder = get_final_output_dir(flat_dataset_tmp, self.task_id)

        infile_1 = flat_dataset_tmp / "recordings" / "converted" / "recording_1.wav"
        outfile_1 = output_folder / "output" / "raw" / "recording_1.csv"

        infile_2 = flat_dataset_tmp / "recordings" / "converted" / "recording_2.wav"
        outfile_2 = output_folder / "output" / "raw" / "recording_2.csv"

        infile_3 = flat_dataset_tmp / "recordings" / "converted" / "recording_3.wav"
        outfile_3 = output_folder / "output" / "raw" / "recording_3.csv"

        (output_folder / "output" / "raw").mkdir(exist_ok=True, parents=True)

        effort_model = W2V2EffortModelMock(
            file_efforts={
                infile_1: 16_000 * 2,
                infile_2: 16_000 * 4,
                infile_3: 16_000 * 3,
            },
            default_file_size=16_000,
        )

        (output_folder / "raw").mkdir(parents=True, exist_ok=True)

        outfile_1.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == 0.0
        )
        outfile_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == 0.0
        )
        outfile_3.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == 1.0
        )


class TestEffortModelNestedDataset:
    effort_model = W2V2EffortModelMock(default_file_size=16_000)
    task_id = UUID("94d1754b-9ce6-435a-b81e-89de666ef3a8")

    def test_find_input_groups(self, nested_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(nested_dataset_tmp)

        assert len(input_groups) == 1
        assert input_groups[0] == [
            nested_dataset_tmp / "recordings" / "converted" / "standard"
        ]

    def test_ogroup_from_igroup(self, nested_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(nested_dataset_tmp)
        input_group = input_groups[0]

        output_folder = get_final_output_dir(nested_dataset_tmp, self.task_id)

        output_group = self.effort_model.ogroup_from_igroup(
            nested_dataset_tmp, input_group, output_folder
        )

        assert len(output_group) == 6

        assert set(output_group) == {
            output_folder / "output" / "raw" / "child_2_day_1_recording.csv",
            output_folder / "output" / "raw" / "child_1_day_1_hour_1_recording.csv",
            output_folder / "output" / "raw" / "child_1_day_2_recording.csv",
            output_folder / "output" / "raw" / "child_2_day_1_hour_1_recording.csv",
            output_folder / "output" / "raw" / "child_1_day_1_recording.csv",
            output_folder / "output" / "raw" / "child_2_day_1_hour_2_recording.csv",
        }

    def test_calculate_progress(self, nested_dataset_tmp: Path):
        output_folder = get_final_output_dir(nested_dataset_tmp, self.task_id)

        infile_1 = (
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_1"
            / "day_1"
            / "recording.wav"
        )
        outfile_1 = output_folder / "output" / "raw" / "child_1_day_1_recording.csv"

        infile_2 = (
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_1"
            / "day_2"
            / "recording.wav"
        )
        outfile_2 = output_folder / "output" / "raw" / "child_1_day_2_recording.csv"

        effort_model = W2V2EffortModelMock(
            file_efforts={
                infile_1: 16_000 * 2,
                infile_2: 16_000 * 4,
            },
            default_file_size=16_000,
        )

        outfile_1.parent.mkdir(parents=True, exist_ok=True)
        outfile_1.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == 0.0
        )

        outfile_2.parent.mkdir(parents=True, exist_ok=True)
        outfile_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == 0.0
        )

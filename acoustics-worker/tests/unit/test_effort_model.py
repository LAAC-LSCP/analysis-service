from pathlib import Path

from analysis_service_core.src.filesystem import UUID, get_final_output_dir

from src.core.effort_model import AcousticsEffortModel


class TestEffortModelFlatDataset:
    effort_model = AcousticsEffortModel()
    task_id = UUID("94d1754b-9ce6-435a-b81e-89de666ef3a8")

    def test_find_input_groups(self, flat_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(flat_dataset_tmp)

        assert len(input_groups) == 1
        igroup = input_groups[0]
        assert set(igroup) == {
            flat_dataset_tmp / "recordings" / "converted" / "recording_1.wav",
            flat_dataset_tmp
            / "annotations"
            / "vtc"
            / "converted"
            / "recording_1_0_1000.csv",
            flat_dataset_tmp / "recordings" / "converted" / "recording_2.wav",
            flat_dataset_tmp
            / "annotations"
            / "vtc"
            / "converted"
            / "recording_2_0_2000.csv",
            flat_dataset_tmp / "recordings" / "converted" / "recording_3.wav",
            flat_dataset_tmp
            / "annotations"
            / "vtc"
            / "converted"
            / "recording_3_0_4000.csv",
        }

    def test_ogroup_from_igroup(self, flat_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(flat_dataset_tmp)

        igroup = input_groups[0]

        output_folder = get_final_output_dir(flat_dataset_tmp, self.task_id)

        output_group = self.effort_model.ogroup_from_igroup(
            flat_dataset_tmp, igroup, output_folder
        )

        set(output_group) == {
            output_folder / "raw" / "recording_1.csv",
            output_folder / "raw" / "recording_2.csv",
            output_folder / "raw" / "recording_3.csv",
        }

    def test_calculate_progress(self, flat_dataset_tmp: Path):
        output_folder = get_final_output_dir(flat_dataset_tmp, self.task_id)

        outfile_1 = output_folder / "raw" / "recording_1.csv"
        outfile_2 = output_folder / "raw" / "recording_2.csv"
        outfile_3 = output_folder / "raw" / "recording_3.csv"

        (output_folder / "raw").mkdir(parents=True, exist_ok=True)

        # 0 progress may seem counterintuitive but the subprocess
        # call handles all the files in one go
        outfile_1.touch()
        assert (
            self.effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == 0.0
        )
        outfile_2.touch()
        assert (
            self.effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == 0.0
        )
        outfile_3.touch()
        assert (
            self.effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == 1.0
        )


class TestEffortModelNestedDataset:
    effort_model = AcousticsEffortModel()
    task_id = UUID("94d1754b-9ce6-435a-b81e-89de666ef3a8")

    def test_find_input_groups(self, nested_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(nested_dataset_tmp)

        assert len(input_groups) == 1
        igroup = input_groups[0]
        assert set(igroup) == {
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_1"
            / "day_1"
            / "hour_1"
            / "recording.wav",
            nested_dataset_tmp
            / "annotations"
            / "vtc"
            / "converted"
            / "child_1"
            / "day_1"
            / "hour_1"
            / "recording_0_3000.csv",
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_1"
            / "day_1"
            / "recording.wav",
            nested_dataset_tmp
            / "annotations"
            / "vtc"
            / "converted"
            / "child_1"
            / "day_1"
            / "recording_0_1000.csv",
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_1"
            / "day_2"
            / "recording.wav",
            nested_dataset_tmp
            / "annotations"
            / "vtc"
            / "converted"
            / "child_1"
            / "day_2"
            / "recording_0_1000.csv",
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_2"
            / "day_1"
            / "hour_1"
            / "recording.wav",
            nested_dataset_tmp
            / "annotations"
            / "vtc"
            / "converted"
            / "child_2"
            / "day_1"
            / "hour_1"
            / "recording_0_1000.csv",
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_2"
            / "day_1"
            / "hour_2"
            / "recording.wav",
            nested_dataset_tmp
            / "annotations"
            / "vtc"
            / "converted"
            / "child_2"
            / "day_1"
            / "hour_2"
            / "recording_0_2000.csv",
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_2"
            / "day_1"
            / "recording.wav",
            nested_dataset_tmp
            / "annotations"
            / "vtc"
            / "converted"
            / "child_2"
            / "day_1"
            / "recording_0_1000.csv",
        }

    def test_ogroup_from_igroup(self, nested_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(nested_dataset_tmp)

        igroup = input_groups[0]

        output_folder = get_final_output_dir(nested_dataset_tmp, self.task_id)

        output_group = self.effort_model.ogroup_from_igroup(
            nested_dataset_tmp, igroup, output_folder
        )

        set(output_group) == {
            output_folder / "raw" / "child_1" / "day_1" / "hour_1" / "recording.csv",
            output_folder / "raw" / "child_1" / "day_1" / "recording.csv",
            output_folder / "raw" / "child_1" / "day_2" / "recording.csv",
            output_folder / "raw" / "child_2" / "day_1" / "hour_1" / "recording.csv",
            output_folder / "raw" / "child_2" / "day_1" / "hour_2" / "recording.csv",
            output_folder / "raw" / "child_2" / "day_1" / "recording.csv",
        }

    def test_calculate_progress(self, nested_dataset_tmp: Path):
        output_folder = get_final_output_dir(nested_dataset_tmp, self.task_id)
        out_files = [
            output_folder / "raw" / "child_1" / "day_1" / "hour_1" / "recording.csv",
            output_folder / "raw" / "child_1" / "day_1" / "recording.csv",
            output_folder / "raw" / "child_1" / "day_2" / "recording.csv",
            output_folder / "raw" / "child_2" / "day_1" / "hour_1" / "recording.csv",
            output_folder / "raw" / "child_2" / "day_1" / "hour_2" / "recording.csv",
            output_folder / "raw" / "child_2" / "day_1" / "recording.csv",
        ]

        out_files[0].parent.mkdir(parents=True, exist_ok=True)
        out_files[0].touch()
        assert (
            self.effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == 0.0
        )

        for i in range(1, 6):
            out_files[i].parent.mkdir(parents=True, exist_ok=True)
            out_files[i].touch()

        assert (
            self.effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == 1.0
        )

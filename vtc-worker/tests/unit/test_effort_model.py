from pathlib import Path

from analysis_service_core.src.filesystem import UUID, get_final_output_dir

from tests.unit.effort_model_mock import VTCEffortModelMock


class TestEffortModelFlatDataset:
    task_id = UUID("94d1754b-9ce6-435a-b81e-89de666ef3a8")

    def test_find_input_groups(self, flat_dataset_tmp: Path):
        effort_model = VTCEffortModelMock(default_file_size=16_000)
        input_groups = effort_model.find_input_groups(flat_dataset_tmp)

        assert len(input_groups) == 3
        assert sorted([[f.name for f in igroup] for igroup in input_groups]) == sorted(
            [
                ["recording_3.wav"],
                ["recording_2.wav"],
                ["recording_1.wav"],
            ]
        )

    def test_ogroup_from_igroup(self, flat_dataset_tmp: Path):
        effort_model = VTCEffortModelMock(default_file_size=16_000)
        input_groups = effort_model.find_input_groups(flat_dataset_tmp)

        rec_1_group = next(
            (
                igroup
                for igroup in input_groups
                if len(igroup) and igroup[0].name == "recording_1.wav"
            ),
            None,
        )

        assert rec_1_group is not None

        output_folder = get_final_output_dir(flat_dataset_tmp, self.task_id)

        output_group = effort_model.ogroup_from_igroup(
            flat_dataset_tmp, rec_1_group, output_folder
        )

        assert output_folder / "raw" / "recording_1.rttm" in output_group

    def test_calculate_progress(self, flat_dataset_tmp: Path):
        output_folder = get_final_output_dir(flat_dataset_tmp, self.task_id)

        infile_1 = (
            flat_dataset_tmp
            / "recordings"
            / "converted"
            / "standard"
            / "recording_1.wav"
        )
        outfile_1 = output_folder / "raw" / "recording_1.rttm"

        infile_2 = (
            flat_dataset_tmp
            / "recordings"
            / "converted"
            / "standard"
            / "recording_2.wav"
        )
        outfile_2 = output_folder / "raw" / "recording_2.rttm"

        infile_3 = (
            flat_dataset_tmp
            / "recordings"
            / "converted"
            / "standard"
            / "recording_3.wav"
        )
        outfile_3 = output_folder / "raw" / "recording_3.rttm"

        effort_model = VTCEffortModelMock(
            file_efforts={
                infile_1: 16_000 * 2,
                infile_2: 16_000 * 4,
                infile_3: 16_000 * 3,
            },
            default_file_size=16_000,
        )

        (output_folder / "raw").mkdir(parents=True, exist_ok=True)

        sum_file_sizes = 2 + 3 + 4

        outfile_1.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == 2 / sum_file_sizes
        )
        outfile_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == (2 + 4) / sum_file_sizes
        )
        outfile_3.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == (2 + 3 + 4) / sum_file_sizes
        )


class TestEffortModelNestedDataset:
    effort_model = VTCEffortModelMock(default_file_size=16_000)
    task_id = UUID("94d1754b-9ce6-435a-b81e-89de666ef3a8")

    def test_find_input_groups(self, nested_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(nested_dataset_tmp)

        assert len(input_groups) == 6
        assert sorted(
            [
                [f.relative_to(nested_dataset_tmp) for f in igroup]
                for igroup in input_groups
            ]
        ) == sorted(
            [
                [Path("recordings/converted/standard/child_1/day_2/recording.wav")],
                [Path("recordings/converted/standard/child_1/day_1/recording.wav")],
                [
                    Path(
                        "recordings/converted/standard/child_1/day_1/"
                        "hour_1/recording.wav"
                    )
                ],
                [Path("recordings/converted/standard/child_2/day_1/recording.wav")],
                [
                    Path(
                        "recordings/converted/standard/child_2/day_1/"
                        "hour_1/recording.wav"
                    )
                ],
                [
                    Path(
                        "recordings/converted/standard/child_2/day_1/"
                        "hour_2/recording.wav"
                    )
                ],
            ]
        )

    def test_ogroup_from_igroup(self, nested_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(nested_dataset_tmp)

        ch_1_day_2 = next(
            (
                igroup
                for igroup in input_groups
                if len(igroup)
                and igroup[0].relative_to(nested_dataset_tmp)
                == Path("recordings/converted/standard/child_1/day_2/recording.wav")
            ),
            None,
        )

        assert ch_1_day_2 is not None

        output_folder = get_final_output_dir(nested_dataset_tmp, self.task_id)

        output_group = self.effort_model.ogroup_from_igroup(
            nested_dataset_tmp, ch_1_day_2, output_folder
        )

        assert (
            output_folder / "raw" / "child_1" / "day_2" / "recording.rttm"
            in output_group
        )

    def test_calculate_progress(self, nested_dataset_tmp: Path):
        output_folder = get_final_output_dir(nested_dataset_tmp, self.task_id)

        infile_1 = (
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "standard"
            / "child_1"
            / "day_1"
            / "recording.wav"
        )
        outfile_1 = output_folder / "raw" / "child_1" / "day_1" / "recording.rttm"

        infile_2 = (
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "standard"
            / "child_1"
            / "day_2"
            / "recording.wav"
        )
        outfile_2 = output_folder / "raw" / "child_1" / "day_2" / "recording.rttm"

        infile_3 = (
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "standard"
            / "child_2"
            / "day_1"
            / "hour_1"
            / "recording.wav"
        )
        outfile_3 = (
            output_folder / "raw" / "child_2" / "day_1" / "hour_1" / "recording.rttm"
        )

        effort_model = VTCEffortModelMock(
            file_efforts={
                infile_1: 16_000 * 2,
                infile_2: 16_000 * 4,
                infile_3: 16_000 * 3,
            },
            default_file_size=16_000,
        )

        sum_file_sizes = 2 + 3 + 4 + 1 * (6 - 3)

        outfile_1.parent.mkdir(parents=True, exist_ok=True)
        outfile_1.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == 2 / sum_file_sizes
        )

        outfile_2.parent.mkdir(parents=True, exist_ok=True)
        outfile_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == (2 + 4) / sum_file_sizes
        )

        outfile_3.parent.mkdir(parents=True, exist_ok=True)
        outfile_3.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == (2 + 3 + 4) / sum_file_sizes
        )

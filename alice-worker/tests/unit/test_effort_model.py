from pathlib import Path

from analysis_service_core.src.filesystem import UUID, get_final_output_dir

from tests.unit.effort_model_mock import ALICEEffortModelMock


class TestEffortModelFlatDataset:
    task_id = UUID("94d1754b-9ce6-435a-b81e-89de666ef3a8")

    def test_find_input_groups(self, flat_dataset_tmp: Path):
        effort_model = ALICEEffortModelMock(default_file_size=16_000)
        input_groups = effort_model.find_input_groups(flat_dataset_tmp)

        assert len(input_groups) == 3
        assert [[f.name for f in igroup] for igroup in input_groups] == [
            ["recording_3.wav"],
            ["recording_2.wav"],
            ["recording_1.wav"],
        ]

    def test_ogroup_from_igroup(self, flat_dataset_tmp: Path):
        effort_model = ALICEEffortModelMock(default_file_size=16_000)
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

        assert len(output_group) == 2
        assert output_folder / "output" / "raw" / "recording_1.txt" in output_group
        assert (
            output_folder / "output" / "extra" / "recording_1_sum.txt" in output_group
        )

    def test_calculate_progress(self, flat_dataset_tmp: Path):
        output_folder = get_final_output_dir(flat_dataset_tmp, self.task_id)

        infile_1 = flat_dataset_tmp / "recordings" / "converted" / "recording_1.wav"
        outfile_1_1 = output_folder / "output" / "raw" / "recording_1.txt"
        outfile_1_2 = output_folder / "output" / "extra" / "recording_1_sum.txt"

        infile_2 = flat_dataset_tmp / "recordings" / "converted" / "recording_2.wav"
        outfile_2_1 = output_folder / "output" / "raw" / "recording_2.txt"
        outfile_2_2 = output_folder / "output" / "extra" / "recording_2_sum.txt"

        infile_3 = flat_dataset_tmp / "recordings" / "converted" / "recording_3.wav"
        outfile_3_1 = output_folder / "output" / "raw" / "recording_3.txt"
        outfile_3_2 = output_folder / "output" / "extra" / "recording_3_sum.txt"

        effort_model = ALICEEffortModelMock(
            file_efforts={
                infile_1: 16_000 * 2,
                infile_2: 16_000 * 4,
                infile_3: 16_000 * 3,
            },
            default_file_size=16_000,
        )

        (output_folder / "output" / "raw").mkdir(parents=True, exist_ok=True)
        (output_folder / "output" / "extra").mkdir(parents=True, exist_ok=True)

        sum_file_sizes = 2 + 3 + 4

        outfile_1_1.touch()
        outfile_1_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == 2 / sum_file_sizes
        )
        outfile_2_1.touch()
        outfile_2_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == (2 + 4) / sum_file_sizes
        )
        outfile_3_1.touch()
        outfile_3_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=flat_dataset_tmp, task_id=self.task_id
            )
            == (2 + 3 + 4) / sum_file_sizes
        )


class TestEffortModelNestedDataset:
    effort_model = ALICEEffortModelMock(default_file_size=16_000)
    task_id = UUID("94d1754b-9ce6-435a-b81e-89de666ef3a8")

    def test_find_input_groups(self, nested_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(nested_dataset_tmp)

        assert len(input_groups) == 6
        assert [
            [f.relative_to(nested_dataset_tmp) for f in igroup]
            for igroup in input_groups
        ] == [
            [Path("recordings/converted/child_1/day_2/recording.wav")],
            [Path("recordings/converted/child_1/day_1/recording.wav")],
            [Path("recordings/converted/child_1/day_1/hour_1/recording.wav")],
            [Path("recordings/converted/child_2/day_1/recording.wav")],
            [Path("recordings/converted/child_2/day_1/hour_1/recording.wav")],
            [Path("recordings/converted/child_2/day_1/hour_2/recording.wav")],
        ]

    def test_ogroup_from_igroup(self, nested_dataset_tmp: Path):
        input_groups = self.effort_model.find_input_groups(nested_dataset_tmp)

        ch_1_day_2 = next(
            (
                igroup
                for igroup in input_groups
                if len(igroup)
                and igroup[0].relative_to(nested_dataset_tmp)
                == Path("recordings/converted/child_1/day_2/recording.wav")
            ),
            None,
        )

        assert ch_1_day_2 is not None

        output_folder = get_final_output_dir(nested_dataset_tmp, self.task_id)

        output_group = self.effort_model.ogroup_from_igroup(
            nested_dataset_tmp, ch_1_day_2, output_folder
        )

        assert len(output_group) == 2
        assert (
            output_folder / "output" / "child_1" / "day_2" / "raw" / "recording.txt"
            in output_group
        )
        assert (
            output_folder
            / "output"
            / "child_1"
            / "day_2"
            / "extra"
            / "recording_sum.txt"
            in output_group
        )

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
        outfile_1_1 = (
            output_folder / "output" / "child_1" / "day_1" / "raw" / "recording.txt"
        )
        outfile_1_2 = (
            output_folder
            / "output"
            / "child_1"
            / "day_1"
            / "extra"
            / "recording_sum.txt"
        )

        infile_2 = (
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_1"
            / "day_2"
            / "recording.wav"
        )
        outfile_2_1 = (
            output_folder / "output" / "child_1" / "day_2" / "raw" / "recording.txt"
        )
        outfile_2_2 = (
            output_folder
            / "output"
            / "child_1"
            / "day_2"
            / "extra"
            / "recording_sum.txt"
        )

        infile_3 = (
            nested_dataset_tmp
            / "recordings"
            / "converted"
            / "child_2"
            / "day_1"
            / "hour_1"
            / "recording.wav"
        )
        outfile_3_1 = (
            output_folder
            / "output"
            / "child_2"
            / "day_1"
            / "hour_1"
            / "raw"
            / "recording.txt"
        )
        outfile_3_2 = (
            output_folder
            / "output"
            / "child_2"
            / "day_1"
            / "hour_1"
            / "extra"
            / "recording_sum.txt"
        )

        effort_model = ALICEEffortModelMock(
            file_efforts={
                infile_1: 16_000 * 2,
                infile_2: 16_000 * 4,
                infile_3: 16_000 * 3,
            },
            default_file_size=16_000,
        )

        sum_file_sizes = 2 + 3 + 4 + 1 * (6 - 3)

        for f in [
            outfile_1_1,
            outfile_1_2,
            outfile_2_1,
            outfile_2_2,
            outfile_3_1,
            outfile_3_2,
        ]:
            f.parent.mkdir(parents=True, exist_ok=True)

        outfile_1_1.touch()
        outfile_1_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == 2 / sum_file_sizes
        )

        outfile_2_1.touch()
        outfile_2_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == (2 + 4) / sum_file_sizes
        )

        outfile_3_1.touch()
        outfile_3_2.touch()
        assert (
            effort_model.get_progress(
                dataset_dir=nested_dataset_tmp, task_id=self.task_id
            )
            == (2 + 3 + 4) / sum_file_sizes
        )

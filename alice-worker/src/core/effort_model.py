from pathlib import Path
from typing import List

from analysis_service_core.src.effort_model import EffortModel, InputGroup, OutputGroup

from src.core.recording_formats import RecordingFormats

SAMPLING_RATE = 16_000


class ALICEEffortModel(EffortModel):
    def find_input_groups(self, dataset_dir: Path) -> List[InputGroup]:
        conv_std_recs = self._get_conv_std_recs(dataset_dir)

        return [
            [f] for f in conv_std_recs.rglob(f"**{RecordingFormats.WAV}") if f.is_file()
        ]

    def ogroup_from_igroup(
        self, dataset_dir: Path, input_group: InputGroup, output_dir: Path
    ) -> List[OutputGroup]:
        converted_recs = self._get_conv_std_recs(dataset_dir)
        audio_file = input_group[0]

        return [
            output_dir
            / "output"
            / audio_file.parent.relative_to(converted_recs)
            / "raw"
            / audio_file.with_suffix(".txt").name,
            output_dir
            / "output"
            / audio_file.parent.relative_to(converted_recs)
            / "extra"
            / audio_file.with_suffix(".txt").with_stem(audio_file.stem + "_sum").name,
        ]

    def effort_from_igroup(self, igroup: InputGroup) -> float:
        audio_file = igroup[0]

        return self._bytes_per_second(audio_file)

    @staticmethod
    def _get_conv_std_recs(dataset_dir: Path) -> Path:
        return dataset_dir / "recordings" / "converted" / "standard"

    def _bytes_per_second(self, file: Path) -> float:
        return file.stat().st_size / SAMPLING_RATE

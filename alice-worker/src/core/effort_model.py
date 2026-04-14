from pathlib import Path
from typing import List

from analysis_service_core.src.effort_model import EffortModel, InputGroup, OutputGroup

from src.core.audio_format import RecordingFormats

SAMPLING_RATE = 16_000


class ALICEEffortModel(EffortModel):
    def find_input_groups(self, dataset_dir: Path) -> List[InputGroup]:
        converted_recs = self._get_converted_recs(dataset_dir)

        subdirs: List[Path] = [
            dir for dir in converted_recs.rglob("**") if dir.is_dir()
        ]
        subdirs_with_recs = filter(VTC2EffortModel._get_audio_files, subdirs)

        return [[subdir] for subdir in subdirs_with_recs]

    def ogroup_from_igroup(
        self, dataset_dir: Path, input_group: InputGroup, output_dir: Path
    ) -> List[OutputGroup]:
        converted_recs = self._get_converted_recs(dataset_dir)
        directory = input_group[0]

        audio_files = VTC2EffortModel._get_audio_files(directory)

        return [
            output_dir / "raw" / f.relative_to(converted_recs).with_suffix(".rttm")
            for f in audio_files
        ]

    def effort_from_igroup(self, igroup: InputGroup) -> float:
        directory = igroup[0]

        return sum(
            map(self._bytes_per_second, VTC2EffortModel._get_audio_files(directory))
        )

    @staticmethod
    def _get_audio_files(dir: Path) -> List[Path]:
        return [
            f for f in dir.iterdir() if f.is_file() and f.suffix in RecordingFormats
        ]

    @staticmethod
    def _get_converted_recs(dataset_dir: Path) -> Path:
        return dataset_dir / "recordings" / "converted"

    def _bytes_per_second(self, file: Path) -> float:
        return file.stat().st_size / SAMPLING_RATE

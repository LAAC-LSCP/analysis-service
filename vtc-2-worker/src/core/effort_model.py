from pathlib import Path
from typing import List

from analysis_service_core.src.effort_model import (
    EffortModel,
    InputGroup,
    OutputGroup,
    PassOutputGroup,
)

from src.core.recording_formats import SAMPLING_RATE, RecordingFormats


class VTC2EffortModel(EffortModel):
    def find_igroups(self, dataset_dir: Path) -> List[InputGroup]:
        converted_recs = self._get_conv_std_recs(dataset_dir)

        subdirs: List[Path] = [
            dir for dir in converted_recs.rglob("**") if dir.is_dir()
        ]
        subdirs_with_recs = filter(VTC2EffortModel._get_audio_files, subdirs)

        return [[subdir] for subdir in subdirs_with_recs]

    def pogroup_from_igroup(
        self, dataset_dir: Path, output_dir: Path, igroup: InputGroup
    ) -> PassOutputGroup:
        converted_recs = self._get_conv_std_recs(dataset_dir)
        directory = igroup[0]
        audio_files = VTC2EffortModel._get_audio_files(directory)

        vtc_output_dir = output_dir / "raw" / directory.relative_to(converted_recs)

        rttm_files = [
            vtc_output_dir / "rttm" / f.with_suffix(".rttm").name for f in audio_files
        ]
        raw_rttm_files = [
            vtc_output_dir / "raw_rttm" / f.with_suffix(".rttm").name
            for f in audio_files
        ]

        return [
            *rttm_files,
            *raw_rttm_files,
            vtc_output_dir / "rttm.csv",
            vtc_output_dir / "raw_rttm.csv",
        ]

    def ogroup_from_pogroup(
        self,
        dataset_dir: Path,
        output_dir: Path,
        pogroup: List[Path],
        igroup: List[Path],
    ) -> OutputGroup:
        return [f.parent.parent / f.name for f in pogroup if f.parent.name == "rttm"]

    def effort_pogroup_from_igroup(
        self, igroup: List[Path], pogroup: List[Path]
    ) -> float:
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
    def _get_conv_std_recs(dataset_dir: Path) -> Path:
        return dataset_dir / "recordings" / "converted" / "standard"

    def _bytes_per_second(self, file: Path) -> float:
        return file.stat().st_size / SAMPLING_RATE

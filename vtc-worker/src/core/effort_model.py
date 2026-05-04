from pathlib import Path
from typing import List

from analysis_service_core.src.effort_model import (
    EffortModel,
    InputGroup,
    OutputGroup,
    PassOutputGroup,
)

from src.core.recording_formats import RecordingFormats

SAMPLING_RATE = 16_000


class VTCEffortModel(EffortModel):
    def find_igroups(self, dataset_dir: Path) -> List[InputGroup]:
        conv_std_recs = self._get_conv_std_recs(dataset_dir)

        return [
            [f] for f in conv_std_recs.rglob(f"**{RecordingFormats.WAV}") if f.is_file()
        ]

    def pogroup_from_igroup(
        self, dataset_dir: Path, output_dir: Path, igroup: InputGroup
    ) -> PassOutputGroup:
        file = igroup[0]

        vtc_base_dir = output_dir / "output_voice_type_classifier"
        vtc_output_dir = vtc_base_dir / file.stem

        output_names = [
            "all.rttm",
            "CHI.rttm",
            "FEM.rttm",
            "KCHI.rttm",
            "MAL.rttm",
            "SPEECH.rttm",
        ]

        return [vtc_output_dir / name for name in output_names]

    def ogroup_from_pogroup(
        self,
        dataset_dir: Path,
        output_dir: Path,
        pogroup: PassOutputGroup,
        igroup: InputGroup,
    ) -> OutputGroup:
        converted_recs_dir = self._get_conv_std_recs(dataset_dir)

        input_file = igroup[0]
        final_filename = input_file.with_suffix(".rttm").name

        return [
            output_dir
            / "raw"
            / input_file.relative_to(converted_recs_dir).parent
            / final_filename
        ]

    def effort_pogroup_from_igroup(
        self, igroup: InputGroup, pogroup: PassOutputGroup
    ) -> float:
        file = igroup[0]

        return self._bytes_per_second(file)

    def _bytes_per_second(self, file: Path) -> float:
        return file.stat().st_size / SAMPLING_RATE

    @staticmethod
    def _get_conv_std_recs(dataset_dir: Path) -> Path:
        return dataset_dir / "recordings" / "converted" / "standard"

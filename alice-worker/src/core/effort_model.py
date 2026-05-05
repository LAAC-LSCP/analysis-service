from pathlib import Path
from typing import List

from analysis_service_core.src.effort_model import EffortModel, InputGroup, OutputGroup, PassOutputGroup

from src.core.recording_formats import RecordingFormats

_SAMPLING_RATE = 16_000


class ALICEEffortModel(EffortModel):
    def find_igroups(self, dataset_dir: Path) -> List[InputGroup]:
        conv_std_recs = self.get_conv_std_recs(dataset_dir)

        return [
            [f] for f in conv_std_recs.rglob(f"**{RecordingFormats.WAV}") if f.is_file()
        ]

    def pogroup_from_igroup(self, dataset_dir: Path, output_dir: Path, igroup: InputGroup) -> PassOutputGroup:
        alice_dir: Path = self.config.get("ALICE_FOLDER")
        return [
            alice_dir / "ALICE_output.txt",
            alice_dir / "ALICE_output_utterances.txt",
            alice_dir / "diarization_output.rttm",
        ]

    def ogroup_from_pogroup(self, dataset_dir: Path, output_dir: Path, pogroup: PassOutputGroup, igroup: InputGroup) -> OutputGroup:
        converted_recs = self.get_conv_std_recs(dataset_dir)
        audio_file = igroup[0]

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
    
    def effort_pogroup_from_igroup(self, igroup: List[Path], pogroup: List[Path]) -> float:
        audio_file = igroup[0]

        return self._bytes_per_second(audio_file)

    @staticmethod
    def get_conv_std_recs(dataset_dir: Path) -> Path:
        return dataset_dir / "recordings" / "converted" / "standard"

    def _bytes_per_second(self, file: Path) -> float:
        return file.stat().st_size / _SAMPLING_RATE

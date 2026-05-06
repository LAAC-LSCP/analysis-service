from pathlib import Path
from typing import List

from analysis_service_core.src.effort_model import (
    EffortModel,
    InputGroup,
    PassOutputGroup,
)

SAMPLING_RATE = 16_000


class W2V2EffortModel(EffortModel):
    def find_igroups(self, dataset_dir: Path) -> List[InputGroup]:
        conv_std_recs = self._get_conv_std_recs(dataset_dir)
        return [[conv_std_recs]]

    def pogroup_from_igroup(
        self, dataset_dir: Path, output_dir: Path, igroup: InputGroup
    ) -> PassOutputGroup:
        conv_std_recs = igroup[0]
        wav_files = [f for f in conv_std_recs.rglob("**.wav") if f.is_file()]
        rel_wav_files = [wav_f.relative_to(conv_std_recs) for wav_f in wav_files]

        return [
            output_dir / "output" / "raw" / "_".join(f.with_suffix(".csv").parts)
            for f in rel_wav_files
        ]

    def ogroup_from_pogroup(
        self,
        dataset_dir: Path,
        output_dir: Path,
        pogroup: PassOutputGroup,
        igroup: InputGroup,
    ) -> List[Path]:
        return pogroup

    def effort_pogroup_from_igroup(
        self, igroup: InputGroup, pogroup: PassOutputGroup
    ) -> float:
        return self._bytes_per_second(igroup[0])

    def _bytes_per_second(self, file: Path) -> float:
        return file.stat().st_size / SAMPLING_RATE

    @staticmethod
    def _get_conv_std_recs(dataset_dir: Path) -> Path:
        return dataset_dir / "recordings" / "converted" / "standard"

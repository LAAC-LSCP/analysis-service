from pathlib import Path
from typing import List

from analysis_service_core.src.effort_model import EffortModel, InputGroup, OutputGroup

SAMPLING_RATE = 16_000


class W2V2EffortModel(EffortModel):
    def find_input_groups(self, dataset_dir: Path) -> List[InputGroup]:
        # NOTE: W2V2 can in fact be adapted to run on small sets of files
        # This coarse-grained approach can be improved upon
        converted_recs = self._get_converted_recs(dataset_dir)

        return [[converted_recs]]

    def ogroup_from_igroup(
        self, dataset_dir: Path, input_group: InputGroup, output_dir: Path
    ) -> List[OutputGroup]:
        converted_recs = input_group[0]
        wav_files = [f for f in converted_recs.rglob("**.wav") if f.is_file()]

        rel_wav_files = [wav_f.relative_to(converted_recs) for wav_f in wav_files]

        return [
            output_dir / "output" / "raw" / "_".join(f.with_suffix(".csv").parts)
            for f in rel_wav_files
        ]

    def effort_from_igroup(self, igroup: InputGroup) -> float:
        return self._bytes_per_second(igroup[0])

    def _bytes_per_second(self, file: Path) -> float:
        return file.stat().st_size / SAMPLING_RATE

    @staticmethod
    def _get_converted_recs(dataset_dir: Path) -> Path:
        return dataset_dir / "recordings" / "converted"

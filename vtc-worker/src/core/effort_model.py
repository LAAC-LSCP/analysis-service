from pathlib import Path
from typing import List

from analysis_service_core.src.effort_model import EffortModel, InputGroup, OutputGroup

from src.core.file_formats import RecordingFormats

SAMPLING_RATE = 16_000


class VTCEffortModel(EffortModel):
    def find_input_groups(self, dataset_dir: Path) -> List[InputGroup]:
        return [
            [f] for f in dataset_dir.rglob(f"**.{RecordingFormats.WAV}") if f.is_file()
        ]

    def ogroup_from_igroup(
        self, dataset_dir: Path, input_group: InputGroup, output_dir: Path
    ) -> List[OutputGroup]:
        converted_recs_dir = dataset_dir / "recordings" / "converted"

        assert len(input_group) == 1

        input_file = input_group[0]
        final_filename = input_file.with_suffix(".rttm").name

        return [
            output_dir
            / "raw"
            / input_file.relative_to(converted_recs_dir).parent
            / final_filename
        ]

    def effort_from_igroup(self, igroup: InputGroup) -> float:
        assert len(igroup) == 1

        return self._bytes_per_second(igroup[0])

    def _bytes_per_second(self, file: Path) -> float:
        return file.stat().st_size / SAMPLING_RATE

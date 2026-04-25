from itertools import chain
from pathlib import Path
from typing import List

from analysis_service_core.src.effort_model import EffortModel, InputGroup, OutputGroup

SAMPLING_RATE = 16_000


class AcousticsEffortModel(EffortModel):
    def find_input_groups(self, dataset_dir: Path) -> List[InputGroup]:
        recs_conv_std = AcousticsEffortModel._get_conv_std_recs(dataset_dir)
        vtc_converted = dataset_dir / "annotations" / "vtc" / "converted"
        recs: List[Path] = [
            f for f in recs_conv_std.rglob("**") if f.is_file() and f.suffix == ".wav"
        ]
        annots: List[Path | None] = [
            AcousticsEffortModel._get_annotation(rec, recs_conv_std, vtc_converted)
            for rec in recs
        ]

        rec_annots = list(
            chain.from_iterable(
                [rec, annot]
                for rec, annot in zip(recs, annots)
                if annot and annot.exists()
            )
        )

        return [rec_annots]

    def ogroup_from_igroup(
        self, dataset_dir: Path, input_group: InputGroup, output_dir: Path
    ) -> List[OutputGroup]:
        recs_converted = AcousticsEffortModel._get_conv_std_recs(dataset_dir)
        recs = [f for f in input_group if f.suffix == ".wav"]

        return [
            output_dir / "raw" / rec.relative_to(recs_converted).with_suffix(".csv")
            for rec in recs
        ]

    def effort_from_igroup(self, igroup: InputGroup) -> float:
        annots = [f for f in igroup if f.suffix == ".csv"]

        return sum(map(AcousticsEffortModel._get_annot_length_s, annots))

    @staticmethod
    def _get_annot_length_s(file: Path) -> float:
        *_, start, end = file.stem.split("_")

        return (int(end) - int(start)) / 1000

    @staticmethod
    def _get_annotation(
        recording: Path, recs_conv_std: Path, annots_converted: Path
    ) -> Path | None:
        rel_rec = recording.relative_to(recs_conv_std)

        annot_dir = (annots_converted / rel_rec).parent

        return next(
            (
                annot
                for annot in annot_dir.iterdir()
                if AcousticsEffortModel._get_rec_name(annot) == recording.name
            ),
            None,
        )

    @staticmethod
    def _get_rec_name(annot: Path) -> str:
        annot_stem = annot.stem
        *rest, _, _ = annot_stem.split("_")

        return "_".join(rest) + ".wav"

    @staticmethod
    def _get_conv_std_recs(dataset_dir: Path) -> Path:
        return dataset_dir / "recordings" / "converted" / "standard"

from itertools import chain
from pathlib import Path
from typing import List

import pandas as pd
from analysis_service_core.src.effort_model import (
    EffortModel,
    InputGroup,
    PassOutputGroup,
)

_VTC = "vtc"


class AcousticsEffortModel(EffortModel):
    def find_igroups(self, dataset_dir: Path) -> List[InputGroup]:
        recs_conv_std = AcousticsEffortModel._get_conv_std_recs(dataset_dir)
        vtc_converted = dataset_dir / "annotations" / _VTC / "converted"
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

    def pogroup_from_igroup(
        self, dataset_dir: Path, output_dir: Path, igroup: InputGroup
    ) -> PassOutputGroup:
        vtc_converted = dataset_dir / "annotations" / _VTC / "converted"
        annots = [f for f in igroup if f.suffix == ".csv"]

        return [
            output_dir / "converted" / annot.relative_to(vtc_converted)
            for annot in annots
        ]

    def ogroup_from_pogroup(
        self,
        dataset_dir: Path,
        output_dir: Path,
        pogroup: List[Path],
        igroup: List[Path],
    ) -> List[Path]:
        recs_converted = AcousticsEffortModel._get_conv_std_recs(dataset_dir)
        recordings = [f for f in igroup if f.suffix == ".wav"]

        return [
            output_dir
            / "raw"
            / recording.relative_to(recs_converted).with_suffix(".csv")
            for recording in recordings
        ]

    def effort_pogroup_from_igroup(
        self, igroup: InputGroup, pogroup: PassOutputGroup
    ) -> float:
        annots = [f for f in igroup if f.suffix == ".csv"]

        return sum(map(AcousticsEffortModel._get_annot_length_s, annots))

    @staticmethod
    def _get_annot_length_s(file: Path) -> float:
        df = pd.read_csv(file)

        return (df["segment_offset"] - df["segment_onset"]).sum() / 1000

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

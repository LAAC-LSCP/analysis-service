from pathlib import Path
from typing import List

from analysis_service_core.testing.mocks.pubsub import PubSubMock
from ChildProject.projects import ChildProject

from src.core.acoustics import Acoustics


class AcousticsMock(Acoustics):
    """
    Test double for acoustics
    """

    def __init__(
        self,
        queue,
        config,
        pubsub=PubSubMock(),
        effort_model=None,
        skip_moving_files=False,
    ):
        super().__init__(queue, config, pubsub, effort_model, skip_moving_files)

    def _derive_annotations(
        self, dataset_dir: Path, _: ChildProject, output_dir: Path
    ) -> None:
        recs_conv_std = dataset_dir / "recordings" / "converted" / "standard"
        vtc_converted = dataset_dir / "annotations" / "vtc" / "converted"
        recs: List[Path] = [
            f for f in recs_conv_std.rglob("**") if f.is_file() and f.suffix == ".wav"
        ]
        annots: List[Path | None] = [
            AcousticsMock._get_annotation(rec, recs_conv_std, vtc_converted)
            for rec in recs
        ]

        for _, annot in zip(recs, annots):
            if annot is None:
                continue

            output_file = output_dir / "converted" / annot.relative_to(vtc_converted)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.touch()

        return

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
                if AcousticsMock._get_rec_name(annot) == recording.name
            ),
            None,
        )

    @staticmethod
    def _get_rec_name(annot: Path) -> str:
        annot_stem = annot.stem
        *rest, _, _ = annot_stem.split("_")

        return "_".join(rest) + ".wav"

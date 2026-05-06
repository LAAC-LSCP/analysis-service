from pathlib import Path

from ChildProject.projects import ChildProject

from src.core.acoustics import Acoustics


class AcousticsMock(Acoustics):
    def _derive_annotations(
        self, dataset_dir: Path, project: ChildProject, output_dir: Path
    ) -> None:
        vtc_converted = dataset_dir / "annotations" / "vtc" / "converted"

        for annot in vtc_converted.rglob("*.csv"):
            output_file = output_dir / "converted" / annot.relative_to(vtc_converted)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.touch()

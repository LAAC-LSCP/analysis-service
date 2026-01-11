import shutil
from dataclasses import dataclass
from pathlib import Path

from analysis_service_core.src.model import ModelPlugin
from ChildProject.annotations import AnnotationManager
from ChildProject.pipelines.derivations import AcousticDerivator
from ChildProject.projects import ChildProject


@dataclass
class Args:
    source: str
    set: str
    threads: int
    overwrite_existing: bool
    format: str


class Acoustics(ModelPlugin):
    def run_model(self, dataset_dir: Path, output_dir: Path) -> None:
        print("Running model...")
        project = ChildProject(dataset_dir)
        am = AnnotationManager(project)

        acoustic_derivator = AcousticDerivator()
        am._derive_annotations(
            "vtc",
            str(output_dir),
            acoustic_derivator,
            overwrite_existing=True,
            output_as_path=True,
        )

        self._make_outputs_raw(output_dir)

        return

    def _make_outputs_raw(self, output_dir) -> None:
        """
        Here we are cheating a little bit. The idea will be that acoustics is
        "just another importation". But for this to work we have to change,
        that is, to use ChildProject's importation utilities, we have to
        1) set "converted" folder to "raw"
        2) rename filenames to remove the duration metadata

        Then Echolalia can run the importation :)
        """
        raw = output_dir / "raw"
        converted = output_dir / "converted"
        if raw.exists():
            shutil.rmtree(raw)

        for file in converted.rglob("*.csv"):
            self._rename_file(file)

        shutil.move(converted, raw)

    def _rename_file(self, file: Path) -> None:
        stem = file.stem
        desired_stem = "_".join(stem.split("_")[0:-2])

        file.rename(file.with_stem(desired_stem))

import shutil
from pathlib import Path

from analysis_service_core.src.effort_model import InputGroup, PassOutputGroup
from analysis_service_core.src.model import ModelPlugin
from ChildProject.annotations import AnnotationManager
from ChildProject.pipelines.derivations import AcousticDerivator
from ChildProject.projects import ChildProject

_VTC = "vtc"


class Acoustics(ModelPlugin):
    def run_model(
        self, dataset_dir: Path, output_dir: Path, igroup: InputGroup
    ) -> None:
        project = ChildProject(dataset_dir)

        self._derive_annotations(dataset_dir, project, output_dir)
        self._logger.info(f"Finished running acoustics in ${dataset_dir!s}!")

    def postprocess(
        self,
        dataset_dir: Path,
        output_dir: Path,
        pogroup: PassOutputGroup,
        igroup: InputGroup,
    ) -> None:
        self._make_outputs_raw(output_dir)

    def _derive_annotations(
        self, dataset_dir: Path, project: ChildProject, output_dir: Path
    ) -> None:
        am = AnnotationManager(project)
        acoustic_derivator = AcousticDerivator()

        try:
            self._logger.info(f"Running acoustics in ${dataset_dir!s}...")
            am._derive_annotations(
                input_set=_VTC,  # TODO: make this parametrisable
                output_set=str(output_dir),
                derivation=acoustic_derivator,  # type: ignore
                overwrite_existing=True,
                output_as_path=True,
            )
        except Exception:
            self._logger.exception("Problem deriving annotations for acoustics")

    def _make_outputs_raw(self, output_dir) -> None:
        """
        Here we are cheating a little bit. The idea will be that acoustics is
        "just another importation". But for this to work we have to change,
        that is, to use ChildProject's importation utilities, we have to
        1) set "converted" folder to "raw"
        2) rename filenames to remove the duration metadata

        Then the ELSI backend can run the importation :)
        """
        raw = output_dir / "raw"
        converted = output_dir / "converted"
        if raw.exists():
            shutil.rmtree(raw)

        for file in converted.rglob("**.csv"):
            self._rename_file(file)

        shutil.move(converted, raw)

    def _rename_file(self, file: Path) -> None:
        stem = file.stem
        desired_stem = "_".join(stem.split("_")[0:-2])

        file.rename(file.with_stem(desired_stem))

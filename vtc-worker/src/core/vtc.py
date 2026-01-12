import shutil
import subprocess
from pathlib import Path
from typing import Set

from analysis_service_core.src.model import ModelPlugin
from analysis_service_core.src.logger import LoggerFactory

from src.core.file_formats import RecordingFormats


logger = LoggerFactory.get_logger(__name__)

VTC_DIR: Path = (
    Path(__file__) / ".." / ".." / ".." / "vtc" / "voice-type-classifier"
).resolve()


class VTC(ModelPlugin):
    def run_model(self, dataset_dir: Path, output_dir: Path) -> None:
        recordings_dir = dataset_dir / "recordings" / "converted"

        if not recordings_dir.exists():
            raise ValueError(
                f"Recordings directory at '{recordings_dir}' does not exist"
            )

        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        audio_files = self._get_audio_files(recordings_dir)

        for file in audio_files:
            self._run_vtc_on_audio_file(recordings_dir, output_dir, file)

        return

    def _run_vtc_on_audio_file(
        self, recordings_dir: Path, output_dir: Path, file: Path
    ) -> None:
        rel_path: Path = file.relative_to(recordings_dir)

        executable: Path = VTC_DIR / "apply.sh"

        bash_script = f"""
        source {self.config.get("CONDA_ACTIVATE_FILE")}
        conda activate {self.config.get("CONDA_ENV_NAME")}
        {str(executable)} {str(file)} --device=gpu
        """

        self._run_subprocess(bash_script, output_dir, file)

        self._move_file(rel_path, output_dir, file)

        return

    def _move_file(self, rel_path: Path, output_dir: Path, input_file: Path) -> None:
        """
        VTC quirks to bear in mind:

        - VTC puts the output files into the same folder as the present working
        directory
        - Puts it under the folder "output_voice_type_classifier/[name of input file]"
        - In there you'll find various outputs. We want "all.rttm"
        """
        vtc_base_dir = output_dir / "output_voice_type_classifier"
        vtc_output_dir = vtc_base_dir / input_file.stem
        all_rttm = vtc_output_dir / "all.rttm"

        if not all_rttm.exists():
            logger.warning(f"Expected output file {all_rttm} not found")
            return

        output_file = (output_dir / rel_path).resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)

        final_output = output_file.with_suffix(".rttm")
        all_rttm.rename(final_output)

        if vtc_base_dir.exists():
            shutil.rmtree(vtc_base_dir)

        return

    def _run_subprocess(self, bash_script: str, output_dir: Path, file: Path) -> None:
        # Note that vtc has a quirk that it puts outputs in the current working dir
        result = subprocess.run(
            ["bash", "-c", bash_script], cwd=output_dir, capture_output=True, text=True
        )

        if result.returncode == 0:
            logger.info(f"Successfully ran VTC on '{str(file)}'")
        else:
            logger.error(f"Error running VTC on '{str(file)}: {result.stderr}")

        return

    def _get_audio_files(self, recordings_dir: Path) -> Set[Path]:
        recording_formats: Set[str] = {r.value for r in RecordingFormats}
        audio_files: Set[Path] = set()

        for format in recording_formats:
            audio_files.update(recordings_dir.rglob(f"*.{format}"))

        return audio_files

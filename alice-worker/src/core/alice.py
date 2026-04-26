import os
import shutil
import subprocess
from pathlib import Path
from typing import Set
from uuid import UUID

from analysis_service_core.src.logger import LoggerFactory
from analysis_service_core.src.model import ModelPlugin

from src.core.recording_formats import RecordingFormats

logger = LoggerFactory.get_logger(__name__)


class ALICE(ModelPlugin):
    def run_model(self, dataset_dir: Path, output_dir: Path, task_id: UUID) -> None:
        output_dir = output_dir / "output"

        conv_std_recs = self._get_conv_std_recs(dataset_dir)

        if not conv_std_recs.exists():
            raise ValueError(
                f"Recordings directory at '{conv_std_recs}' does not exist"
            )

        audio_files = self._get_audio_files(conv_std_recs)

        for file in audio_files:
            self._run_alice_on_audio_file(conv_std_recs, output_dir, file)
            self.report_progress(dataset_dir, task_id)

    def _run_alice_on_audio_file(
        self, recordings_dir: Path, output_dir: Path, file: Path
    ) -> None:
        logger.info(f"Running ALICE on {recordings_dir!s}")
        rel_path: Path = file.relative_to(recordings_dir)

        executable: Path = self.alice_dir / "run_ALICE.sh"

        device_str: str = ""
        if self.config.get("ALICE_DEVICE") == "gpu":
            device_str = "gpu"

        bash_script = f"""
        source {self.config.get("CONDA_ACTIVATE_FILE")}
        conda activate {self.config.get("CONDA_ENV_NAME")}
        {str(executable)} {str(file)} {device_str}
        """

        return_code = self._run_subprocess(bash_script, self.alice_dir, file)

        if return_code == 0:
            self._move_and_clean_outputs(rel_path, output_dir)

        return

    def _run_subprocess(self, bash_script: str, alice_dir: Path, file: Path) -> int:
        # NOTE: ALICE has a quirk that it cannot run if your PWD is not the
        # ALICE folder itself
        result = subprocess.run(
            ["bash", "-c", bash_script],
            cwd=alice_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logger.info(f"Successfully ran ALICE on '{file!s}'")
        else:
            logger.error(f"Error running ALICE on '{file!s}: {result.stderr}")

        return result.returncode

    def _move_and_clean_outputs(self, rel_path: Path, output_dir: Path) -> None:
        rel_path_dir = rel_path.parent
        base_name = rel_path.stem

        raw_folder = output_dir / rel_path_dir / "raw"
        sum_folder = output_dir / rel_path_dir / "extra"

        if not raw_folder.exists():
            raw_folder.mkdir(parents=True, exist_ok=True)
        if not sum_folder.exists():
            sum_folder.mkdir(parents=True, exist_ok=True)

        shutil.move(
            self.alice_dir / "ALICE_output.txt", sum_folder / f"{base_name}_sum.txt"
        )
        shutil.move(
            self.alice_dir / "ALICE_output_utterances.txt",
            raw_folder / f"{base_name}.txt",
        )
        # VTC output (VTC is a submodule of the ALICE model)
        diarization_output = self.alice_dir / "diarization_output.rttm"

        if diarization_output.exists():  # Don't change this line!
            os.remove(self.alice_dir / "diarization_output.rttm")

        return

    def _get_audio_files(self, recordings_dir: Path) -> Set[Path]:
        audio_files: Set[Path] = set()

        for format in RecordingFormats:
            audio_files.update(recordings_dir.rglob(f"**{format}"))

        return audio_files

    @staticmethod
    def _get_conv_std_recs(dataset_dir: Path) -> Path:
        return dataset_dir / "recordings" / "converted" / "standard"

    @property
    def alice_dir(self) -> Path:
        return self.config.get("ALICE_FOLDER")

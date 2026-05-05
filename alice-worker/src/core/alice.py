import os
import shutil
import subprocess
from pathlib import Path

from analysis_service_core.src.effort_model import InputGroup, PassOutputGroup
from analysis_service_core.src.logger import LoggerFactory
from analysis_service_core.src.model import ModelPlugin

from src.core.effort_model import ALICEEffortModel

logger = LoggerFactory.get_logger(__name__)


class ALICE(ModelPlugin):
    def run_model(self, dataset_dir: Path, output_dir: Path, igroup: InputGroup) -> None:
        final_output_dir = output_dir / "output"
        conv_std_recs = ALICEEffortModel.get_conv_std_recs(dataset_dir)
        audio_file = igroup[0]
        self._run_alice_on_audio_file(conv_std_recs, final_output_dir, audio_file)

    def _run_alice_on_audio_file(
        self, recordings_dir: Path, final_output_dir: Path, file: Path
    ) -> None:
        logger.info(f"Running ALICE on {recordings_dir!s}")
        executable: Path = self.alice_dir / "run_ALICE.sh"

        device_str: str = ""
        if self.config.get("ALICE_DEVICE") == "gpu":
            device_str = "gpu"

        bash_script = f"""
        source {self.config.get("CONDA_ACTIVATE_FILE")}
        conda activate {self.config.get("CONDA_ENV_NAME")}
        {str(executable)} {str(file)} {device_str}
        """

        self._run_subprocess(bash_script, self.alice_dir, file)

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

    def postprocess(self, dataset_dir: Path, output_dir: Path, pogroup: PassOutputGroup, igroup: InputGroup) -> None:
        conv_std_recs = ALICEEffortModel.get_conv_std_recs(dataset_dir)
        audio_file = igroup[0]
        rel_path: Path = audio_file.relative_to(conv_std_recs)
        final_output_dir = output_dir / "output"

        rel_path_dir = rel_path.parent
        base_name = rel_path.stem

        raw_folder = final_output_dir / rel_path_dir / "raw"
        sum_folder = final_output_dir / rel_path_dir / "extra"

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

    @property
    def alice_dir(self) -> Path:
        return self.config.get("ALICE_FOLDER")

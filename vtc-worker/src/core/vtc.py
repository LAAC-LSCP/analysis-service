import shutil
import subprocess
from pathlib import Path

from analysis_service_core.src.effort_model import InputGroup, PassOutputGroup
from analysis_service_core.src.logger import LoggerFactory
from analysis_service_core.src.model import ModelPlugin

from src.core.effort_model import VTCEffortModel

logger = LoggerFactory.get_logger(__name__)


class VTC(ModelPlugin):
    def run_model(
        self, dataset_dir: Path, output_dir: Path, igroup: InputGroup
    ) -> None:
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        file = igroup[0]
        self._run_vtc_on_audio_file(output_dir, file)

    def postprocess(
        self,
        dataset_dir: Path,
        output_dir: Path,
        pogroup: PassOutputGroup,
        igroup: InputGroup,
    ) -> None:
        """
        VTC quirks to bear in mind:

        - VTC puts the output files into the same folder as the present working
        directory
        - Puts it under the folder "output_voice_type_classifier/[name of input file]"
        - In there you'll find various outputs. We want "all.rttm"
        """
        input_file = igroup[0]
        all_rttm = next((f for f in pogroup if f.name == "all.rttm"), None)

        if not all_rttm:
            logger.warning(f"Expected output file {all_rttm!s} not found")
            return

        output_file = (
            output_dir
            / "raw"
            / input_file.relative_to(VTCEffortModel._get_conv_std_recs(dataset_dir))
        ).resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)

        final_output = output_file.with_suffix(".rttm")
        all_rttm.rename(final_output)

        vtc_base_dir = output_dir / "output_voice_type_classifier"
        if vtc_base_dir.exists():
            shutil.rmtree(vtc_base_dir)

        return

    def _run_vtc_on_audio_file(self, output_dir: Path, file: Path) -> None:
        executable: Path = self._get_apply_sh()

        device_str: str = ""
        device = self.config.get("VTC_DEVICE")
        if device == "gpu":
            device_str = "--device=gpu"

        bash_script = f"""
        source {self.config.get("CONDA_ACTIVATE_FILE")}
        conda activate {self.config.get("CONDA_ENV_NAME")}
        {str(executable)} {str(file)} {device_str}
        """

        self._run_subprocess(bash_script, output_dir, file)

    def _get_apply_sh(self) -> Path:
        return self.config.get("VTC_FOLDER") / "apply.sh"

    def _run_subprocess(self, bash_script: str, output_dir: Path, file: Path) -> None:
        # Note that vtc has a quirk that it puts outputs in the current working dir
        result = subprocess.run(
            ["bash", "-c", bash_script], cwd=output_dir, capture_output=True, text=True
        )

        if result.returncode == 0:
            logger.info(f"Successfully ran VTC on '{file!s}'")
        else:
            logger.error(f"Error running VTC on '{file!s}: {result.stderr}")

        return

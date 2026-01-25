import os
import shutil
import subprocess
from pathlib import Path

from analysis_service_core.src.logger import LoggerFactory
from analysis_service_core.src.model import ModelPlugin

from src.core.audio_format import AudioFormat

logger = LoggerFactory.get_logger(__name__)


class VTC_2(ModelPlugin):
    def run_model(self, dataset_dir: Path, output_dir: Path) -> None:
        recordings_path = dataset_dir / "recordings" / "converted"
        self._do_vtc(recordings_path, output_dir / "raw")

        return

    def _do_vtc(self, input: Path, output: Path) -> None:
        sub_dirs = [dir for dir in input.iterdir() if dir.is_dir()]
        files = [
            f for f in input.iterdir() if f.is_file() and f.suffix in list(AudioFormat)
        ]

        if len(files):
            logger.info(f"Calling VTC 2 in folder {str(input)}")
            return_code = self._call_vtc(input, output)

            if return_code == 0:
                logger.info(f"VTC 2 successfully run in folder {str(input)}")
                self._move_and_clean(output)
            else:
                logger.error(f"Problem running VTC 2 in folder {str(input)}")

        for dir in sub_dirs:
            self._do_vtc(dir, output / dir.name)

        return

    def _move_and_clean(self, dir: Path) -> None:
        raw_rttm_dir = dir / "raw_rttm"
        shutil.rmtree(raw_rttm_dir)

        for csv_name in ["raw_rttm.csv", "rttm.csv"]:
            csv_path = dir / csv_name
            csv_path.unlink()

        rttm_dir = dir / "rttm"
        for item in rttm_dir.iterdir():
            shutil.move(str(item), str(dir / item.name))

        rttm_dir.rmdir()

        return

    def _call_vtc(self, input: Path, output: Path) -> int:
        vtc_folder = self.config.get("VTC_2_FOLDER")
        device = self.config.get("VTC_2_DEVICE")
        bash_script = f"""
        uv run scripts/infer.py --wavs {str(input)} --output {str(output)} \
--device={device}
        """

        return self._run_subprocess(bash_script, vtc_folder, input, output)

    def _run_subprocess(
        self, bash_script: str, cwd: Path, input_dir: Path, output_dir: Path
    ) -> int:
        vtc_venv = self.config.get("VTC_2_FOLDER") / ".venv"

        # Note that vtc 2 has a quirk that it puts outputs in the current working dir
        result = subprocess.run(
            ["bash", "-c", bash_script],
            cwd=cwd,
            capture_output=True,
            text=True,
            env={
                "VIRTUAL_ENV": str(vtc_venv),
                "PATH": f"{vtc_venv}/bin:" + os.environ["PATH"],
            },
        )

        if result.returncode == 0:
            logger.info(f"Successfully ran VTC 2 on folder '{str(input_dir)}'")
        else:
            logger.error(f"Error running VTC 2 on folder '{str(input_dir)} with output \
'{str(output_dir)}': {result.stderr}")

        return result.returncode

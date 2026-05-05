import os
import shutil
import subprocess
from pathlib import Path

from analysis_service_core.src.effort_model import InputGroup, PassOutputGroup
from analysis_service_core.src.model import (
    ModelPlugin,
)

from src.core.effort_model import VTC2EffortModel


class VTC2(ModelPlugin):
    def run_model(
        self, dataset_dir: Path, output_dir: Path, igroup: InputGroup
    ) -> None:
        directory = igroup[0]

        conv_std_recs = VTC2EffortModel._get_conv_std_recs(dataset_dir)
        final_output_dir = output_dir / "raw" / directory.relative_to(conv_std_recs)

        return_code = self._call_vtc(directory, final_output_dir)
        if return_code == 0:
            self._logger.info(f"VTC 2 successfully run in folder {conv_std_recs!s}")

    def postprocess(
        self,
        dataset_dir: Path,
        output_dir: Path,
        pogroup: PassOutputGroup,
        igroup: InputGroup,
    ) -> None:
        directory = igroup[0]

        conv_std_recs = VTC2EffortModel._get_conv_std_recs(dataset_dir)
        final_output_dir = output_dir / "raw" / directory.relative_to(conv_std_recs)

        self._logger.info("Moving outputs")
        self._move_and_clean(final_output_dir)

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

        # NOTE that VTC 2 has a quirk that it puts outputs in the cwd
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
            self._logger.info(f"Successfully ran VTC 2 on folder '{input_dir!s}'")
        else:
            self._logger.error(
                f"Error running VTC 2 on folder '{input_dir!s} with output \
'{output_dir!s}': {result.stderr}"
            )

        return result.returncode
